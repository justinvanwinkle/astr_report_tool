from os.path import join
from os.path import abspath
from glob import iglob

from astropy.coordinates import SkyCoord
from astropy.io import fits


class FitsCentroid:
    def __init__(self, fn, hdu_index, decl, ra):
        self.fn = fn
        self.hdu_index = hdu_index
        self.decl = decl
        self.ra = ra

        self.coord = SkyCoord(ra, decl, frame='fk5', unit="deg")

    @classmethod
    def from_file(cls, basepath, fn):
        with fits.open(fn, mmap=True) as f:
            for ix, hdu in enumerate(f):
                ra = hdu.header['CRVAL1']
                decl = hdu.header['CRVAL2']
                yield cls(fn, ix, ra, decl)

    def to_row(self):
        return [self.fn, self.hdu_index, self.decl, self.ra]


class FitsIndex:
    def __init__(self, path):
        self.path = abspath(path)
        self.index_fn = join(path, '.fits_centroid.index')

    def generate_index(self):
        d = {}
        with open(self.index_fn, 'w') as f:
            for fn in iglob(join(self.path, '**/*.fits'), recursive=True):
                for centroid in FitsCentroid.from_file(self.path, fn):
                    pass
