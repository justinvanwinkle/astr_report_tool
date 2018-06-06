from io import BytesIO

from astropy.units import deg
from astropy.wcs import WCS
from astroquery.skyview import SkyView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
import numpy as np


class AtlasTrackGraphic:
    def __init__(self, ephemerides):
        self.ephemerides = ephemerides

    def render(self, cmap_name='plasma', sigma_low=1, sigma_high=7):
        graphic = overlayed_atlas_graphic(
            self.ephemerides, cmap_name, sigma_low, sigma_high)

        return graphic


def get_atlas_img(position, radius, survey='2MASS-K'):
    imgs = SkyView.get_images(position=position,
                              survey=[survey],
                              radius=radius)

    img = imgs[0]

    return img


def build_overlay(img,
                  ephemerides,
                  lower_sigma=1,
                  upper_sigma=7,
                  cmap='plasma',
                  format='png'):
    wcs = WCS(img[0].header)
    image_data = img[0].data
    buf = BytesIO()

    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111, projection=wcs)

    mean = np.mean(image_data)
    stdev = np.std(image_data)
    upper = mean + upper_sigma * stdev
    lower = mean - lower_sigma * stdev

    ax.imshow(image_data, cmap=cmap, norm=LogNorm(vmin=lower, vmax=upper))

    def add_marker(eph, color, marker):
        ax.scatter(eph.RA,
                   eph.decl,
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


def overlayed_atlas_graphic(ephemerides, cmap_name, sigma_low, sigma_high):
    img = get_atlas_img(ephemerides.first.coordinate,
                        max(ephemerides.span() * 3, .1 * deg))
    graphic = build_overlay(img, ephemerides, sigma_low, sigma_high, cmap_name)

    return graphic
