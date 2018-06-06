from json import dumps

from werkzeug import Response
from matplotlib.cm import cmap_d
# from astropy.coordinates import EarthLocation

from ..lib.render import render
from ..lib.neo_list import get_neos
from ..lib.neo_list import NEOCPEntry
from ..lib.neo_track import AtlasTrackGraphic
from ..lib.observatory_list import Observatory
from ..lib.observatory_list import get_observatories
from ..lib.minorplanet_scrape import EphemeridesRequest
from ..lib.render import to_data_uri


_cmap_list = [k for k in cmap_d if not k.endswith('_r')]
_cmap_list.sort()


def neo_lookup(req):
    ctx = dict(product_name='neo_lookup')
    ctx['neos'] = neos = get_neos()
    ctx['neo_names'] = [n.temporary_designation for n in neos]
    ctx['NEOCPEntry'] = NEOCPEntry

    ctx['Observatory'] = Observatory
    ctx['observatories'] = get_observatories()

    ctx['cmap_list'] = _cmap_list

    return Response(
        render('html/neo_lookup.html', context=ctx),
        mimetype='text/html')


def ajax_object_track(req):
    obj_name = req.values.get('obj')
    latitude = req.values.get('latitude', type=float)
    longitude = req.values.get('longitude', type=float)

    # todo add configuration to dry up defaults
    cmap_name = req.values.get('cmap_name')
    sigma_high = req.values.get('sigma_high', type=int)
    sigma_low = req.values.get('sigma_low', type=int)

    ephemerides_req = EphemeridesRequest(longitude, latitude, obj_name)
    ephemerides = ephemerides_req.make_request()

    atg = AtlasTrackGraphic(ephemerides)
    encoded_graphic = to_data_uri(
        atg.render(cmap_name, sigma_low, sigma_high), 'image/png')

    ephemeride_table = render("html/ephemeride_table.html",
                              dict(ephemerides=ephemerides))

    return Response(
        dumps(dict(graphic=encoded_graphic,
                   ephemeride_table=ephemeride_table)),
        mimetype='application/json')


def fits_histogram(req):
    pass
