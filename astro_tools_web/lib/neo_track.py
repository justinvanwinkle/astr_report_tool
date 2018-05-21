from io import BytesIO

from astropy.coordinates import SkyCoord
from astropy.units import deg
from astropy.wcs import WCS
from astroquery.skyview import SkyView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
import numpy as np

from .. lib.render import render
from .. lib.neo_list import get_neos
from .. lib.neo_list import NEOCPEntry
from .. lib.observatory_list import Observatory
from .. lib.observatory_list import get_observatories
from ..lib.minorplanet_scrape import EphemeridesRequest


def get_atlas_img(position, radius, survey='2MASS-K'):
    imgs = SkyView.get_images(position=position,
                              survey=[survey],
                              radius=radius)

    img = imgs[0]

    return img


def build_overlay(img, ephemerides, format='png'):
    eph = ephemerides.ephemerides[0]
    position = SkyCoord(float(eph['RA']) * deg, float(eph['decl']) * deg)
    radius = max(ephemerides.span(5) * 3, .1 * deg)
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

    ax.imshow(image_data, cmap='plasma', norm=LogNorm(vmin=lower, vmax=upper))

    def add_marker(eph, color, marker):
        ax.scatter(float(eph['RA']),
                   float(eph['decl']),
                   marker=marker,
                   transform=ax.get_transform('fk5'),
                   s=30,
                   edgecolor=color,
                   facecolor='none')

    for eph in ephemerides.rest:
        add_marker(eph, 'red', '.')
    add_marker(ephemerides.first, 'green', 'X')

    fig.savefig(buf, format=format, dpi=200)
    return buf.getvalue()


def overlayed_atlas_image(ephemerides):
