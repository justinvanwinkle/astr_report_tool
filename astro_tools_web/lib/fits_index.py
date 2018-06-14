from os.path import join
from os.path import abspath
from os.path import relpath
from glob import iglob
from json import dump as json_dump

from astropy.coordinates import SkyCoord
from astropy.io import fits

from .encodable import Encodable


class FitsCentroid(Encodable):
    _encode_attrs = ('fn', 'hdu_index', 'decl', 'ra')

    def __init__(self, path, fn, hdu_index, ra, decl):
        self.path = path
        self.fn = fn
        self.hdu_index = hdu_index
        self.ra = ra
        self.decl = decl

        self.coord = SkyCoord(ra=ra, dec=decl, frame='icrs', unit="deg")

    @property
    def abs_fn(self):
        return join(self.path, self.fn)

    @classmethod
    def from_file(cls, basepath, fn):
        abs_fn = join(basepath, fn)
        with fits.open(abs_fn, mmap=True) as f:
            for ix, hdu in enumerate(f):
                ra = hdu.header['CRVAL1']
                decl = hdu.header['CRVAL2']
                yield cls(basepath, fn, ix, ra, decl)


class FitsIndex:
    def __init__(self, path):
        self.path = abspath(path)
        self.index_fn = join(path, '.fits_centroid.index')
        self.entries = []

    def reindex_path(self):
        entries = []
        for fn in iglob(join(self.path, '**/*.fits'), recursive=True):
            for centroid in FitsCentroid.from_file(
                    self.path, relpath(fn, self.path)):
                entries.append(centroid)
        self.entries = entries

    def write_index(self, fn=None):
        if fn is None:
            fn = self.index_fn
        encoded_entries = []
        index = dict(encoded_entries=encoded_entries)
        for entry in self.entries:
            encoded_entries.append(entry.to_dict())

        with open(fn, 'w') as f:
            json_dump(index, f, indent=2)
