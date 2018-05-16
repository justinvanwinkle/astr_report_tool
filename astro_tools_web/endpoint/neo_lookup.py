# -*- coding: utf-8 -*-
from json import dumps
from io import BytesIO
from multiprocessing import Process
from multiprocessing import Pipe

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.units import deg
from astropy.visualization import astropy_mpl_style
from astropy.wcs import WCS
from astroquery.skyview import SkyView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from werkzeug import Response
import numpy as np

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
    position = SkyCoord(float(eph['RA']) * deg, float(eph['decl']) * deg)
    imgs = SkyView.get_images(position=position,
                              survey=['2MASS-K'],
                              radius=max(ephemerides.span(5) * 3, .1 * deg))

    print('found {} images, {} ephemerides'.format(
        len(imgs), len(ephemerides.ephemerides)))
    # TODO: fix this
    img = imgs[0]
    parent, child = Pipe()
    # p = Process(target=make_image, args=(ephemerides, img, child))
    # p.start()
    # p.join()
    # result = parent.recv()
    wcs = WCS(img[0].header)
    image_data = img[0].data
    buf = BytesIO()

    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111, projection=wcs)

    mean = np.mean(image_data)
    stdev = np.std(image_data)
    upper = mean + 7 * stdev
    lower = mean - stdev

    ax.imshow(image_data,
              cmap='plasma',
              norm=LogNorm(
                  vmin=lower,
                  vmax=upper))

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

    fig.savefig(buf, format='png', dpi=200)
    return Response(buf.getvalue(), mimetype="image/png")


def fits_histogram(req):
    pass
