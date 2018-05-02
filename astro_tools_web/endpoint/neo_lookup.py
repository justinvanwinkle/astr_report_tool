# -*- coding: utf-8 -*-
from json import dumps
from io import BytesIO
from multiprocessing import Process
from multiprocessing import Pipe

from werkzeug import Response
from astropy.io import fits
import matplotlib.pyplot as plt
from astroquery.skyview import SkyView
from astropy.wcs import WCS
from astropy.visualization import astropy_mpl_style
from matplotlib.patches import Circle
from astropy.units import deg

from .. lib.render import render
from .. lib.neo_list import get_neos
from .. lib.neo_list import NEOCPEntry
from .. lib.observatory_list import Observatory
from .. lib.observatory_list import get_observatories
from ..lib.minorplanet_scrape import EphemeridesRequest


def neo_lookup(req):
    ctx = dict(product_name='neo_lookup')
    ctx['neos'] = get_neos()
    ctx['NEOCPEntry'] = NEOCPEntry

    ctx['Observatory'] = Observatory
    ctx['observatories'] = get_observatories()

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


def object_track(req):
    obj_name = req.values.get('obj')
    latitude = req.values.get('latitude', type=float)
    longitude = req.values.get('longitude', type=float)
    ephemerides_req = EphemeridesRequest(longitude, latitude, obj_name)
    ephemerides = ephemerides_req.make_request()

    eph = ephemerides.ephemerides[0]

    imgs = SkyView.get_images(position='%sd %sd' % (eph['RA'], eph['decl']),
                              survey=['2MASS-K'],
                              radius=max(ephemerides.span(5) * 3, .1 * deg))

    print('found {} images'.format(len(imgs)))
    # TODO: fix this
    img = imgs[0]
    parent, child = Pipe()
    p = Process(target=make_image, args=(ephemerides, img, child))
    p.start()
    p.join()
    result = parent.recv()

    return Response(result, mimetype="image/png")


def make_image(ephemerides, img, conn):
    wcs = WCS(img[0].header)
    image_data = img[0].data
    buf = BytesIO()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection=wcs)
    ax.imshow(image_data, cmap='viridis')
    for ix, eph in reversed(list(enumerate(ephemerides.ephemerides))):
        if ix == 0:
            color = 'green'
            marker = 'X'
        else:
            color = 'red'
            marker = '.'
        ax.scatter(float(eph['RA']), float(eph['decl']),
                   marker=marker,
                   transform=ax.get_transform('fk5'),
                   s=30,
                   edgecolor=color, facecolor='none')
    # fig.tight_layout()

    fig.savefig(buf, format='png', dpi=200)
    conn.send(buf.getvalue())
