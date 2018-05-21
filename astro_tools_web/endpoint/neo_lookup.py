from json import dumps
from base64 import encodebytes

from werkzeug import Response
from matplotlib.cm import cmap_d
# from astropy.coordinates import EarthLocation

from ..lib.render import render
from ..lib.neo_list import get_neos
from ..lib.neo_list import NEOCPEntry
from ..lib.neo_track import overlayed_atlas_graphic
from ..lib.observatory_list import Observatory
from ..lib.observatory_list import get_observatories
from ..lib.minorplanet_scrape import EphemeridesRequest


_cmap_list = [k for k in cmap_d if not k.endswith('_r')]


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


def neo_ephemerides(req):
    obj_name = req.values.get('obj')
    ephemerides_req = EphemeridesRequest(76.888186, 38.9974385, obj_name)
    ephemerides = ephemerides_req.make_request()

    return Response(
        dumps(ephemerides),
        mimetype="application/json")


def ajax_object_track(req):
    print(req.values)
    obj_name = req.values.get('obj')
    latitude = req.values.get('latitude', type=float)
    longitude = req.values.get('longitude', type=float)

    ephemerides_req = EphemeridesRequest(longitude, latitude, obj_name)
    ephemerides = ephemerides_req.make_request()

    graphic = overlayed_atlas_graphic(ephemerides)
    encoded_graphic = encodebytes(graphic).decode()
    encoded_graphic = 'data:image/png;base64,{}'.format(encoded_graphic)

    return Response(
        dumps(dict(graphic=encoded_graphic)),
        mimetype='application/json')


def object_track(req):
    obj_name = req.values.get('obj')
    latitude = req.values.get('latitude', type=float)
    longitude = req.values.get('longitude', type=float)

    # location = EarthLocation.from_geodetic(longitude, latitude)
    ephemerides_req = EphemeridesRequest(longitude, latitude, obj_name)
    ephemerides = ephemerides_req.make_request()

    graphic = overlayed_atlas_graphic(ephemerides)

    return Response(graphic, mimetype="image/png")


def fits_histogram(req):
    pass
