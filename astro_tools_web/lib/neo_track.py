from io import BytesIO

from astropy.units import deg
from astropy.wcs import WCS
from astropy.io import fits
from astropy.nddata.utils import Cutout2D
#from astroquery.skyview import SkyView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
import numpy as np

from .fits_index import FitsIndex

_fits_index = FitsIndex('/home/jvanwink/fits/')
_fits_index.load_index()


class AtlasTrackGraphic:
    def __init__(self, ephemerides):
        self.ephemerides = ephemerides

    def render(self, cmap_name='plasma', sigma_low=1, sigma_high=7):
        graphic = overlayed_atlas_graphic(
            self.ephemerides, cmap_name, sigma_low, sigma_high)

        return graphic


def build_overlay(ephemerides,
                  lower_sigma=1,
                  upper_sigma=7,
                  cmap='plasma',
                  radius=None,
                  format='png'):

    position = ephemerides.first.coordinate
    img = fits.open(_fits_index.closest_image(position).abs_fn, mmap=True)

    cutout = Cutout2D(img[0].data,
                      position,
                      size=radius*2,
                      wcs=WCS(img[0].header))

    # wcs = WCS(img[0].header)
    # image_data = img[0].data

    wcs = cutout.wcs
    image_data = cutout.data

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
    graphic = build_overlay(ephemerides,
                            sigma_low,
                            sigma_high,
                            cmap_name,
                            radius=max(ephemerides.span() * 3, .1 * deg))
    return graphic
