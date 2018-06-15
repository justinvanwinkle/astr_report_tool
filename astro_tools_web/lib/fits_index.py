from os.path import join
from os.path import abspath
from os.path import relpath
from glob import iglob
from json import dump as json_dump
from json import load as json_load
from numpy import sin
from numpy import cos
from numpy import pi
from scipy.spatial import KDTree

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
    _index_fn = '.fits_centroid.index'

    def __init__(self, path):
        self.path = abspath(path)
        self.index_fn = join(path, self._index_fn)
        self.entries = []

        self.kd_index = None

    def reindex_path(self):
        entries = []
        for fn in iglob(join(self.path, '**/*.fits'), recursive=True):
            for centroid in FitsCentroid.from_file(
                    self.path, relpath(fn, self.path)):
                entries.append(centroid)
        self.entries = entries
        self.rebuild_index()

    def rebuild_index(self):
        theta = [e.decl * pi/180 for e in self.entries]
        phi = [e.ra * pi/180 for e in self.entries]

        x = cos(theta) * sin(phi)
        y = sin(theta) * sin(phi)
        z = cos(phi)

        self.kd_index = KDTree(list(zip(x, y, z)))

    def write_index(self, fn=None):
        if fn is None:
            fn = self.index_fn
        encoded_entries = []
        index = dict(encoded_entries=encoded_entries)
        for entry in self.entries:
            encoded_entries.append(entry.to_dict())

        with open(fn, 'w') as f:
            json_dump(index, f, indent=2)

    def load_index(self):
        with open(self.index_fn) as f:
            index = json_load(f)
        entries = []
        for d in index['encoded_entries']:
            d['path'] = self.path
            entries.append(FitsCentroid(**d))
        self.entries = entries

    def closest_image(self, coord):
        ra = coord.ra
        dec = coord.dec
        x = cos(dec) * sin(ra)
        y = sin(dec) * sin(ra)
        z = cos(ra)

        _, index = self.kd_index.query((x, y, z))

        return self.entries[index]
