from urllib.request import urlopen
from datetime import datetime

from werkzeug.urls import url_encode
from astropy import units as u
from astropy.coordinates import SkyCoord

from .html_scrape import Document


class EphemeridesRequest:
    _url = 'https://cgi.minorplanetcenter.net/cgi-bin/confirmeph2.cgi'

    def __init__(self, longitude, latitude, altitude=None, obscode=None):
        self.longitude = longitude
        self.latitude = latitude
        if longitude is not None and self.longitude < 0:
            self.longitude += 360

        self.altitude = altitude
        self.obscode = obscode

    def data(self):
        return dict(sort='d',
                    W='a',
                    obscode=self.obscode if self.obscode else '',
                    Parallax=1,
                    long=self.longitude,
                    lat=self.latitude,
                    alt=self.altitude if self.altitude is not None else '',
                    int=2,
                    start=0,
                    raty='d',
                    mot='m',
                    dmot='p',
                    out='f',
                    sun='x',
                    oalt=20)

    def make_request(self):
        print(self.data())
        s = urlopen(
            self._url, data=url_encode(self.data()).encode('utf8')).read()
        s = s.decode('utf8')
        return EphemeridesSet.from_minorplanets_tool(s)


class Ephemeris:

    def __init__(self, timestamp, RA, decl, elongation, V):
        self.timestamp = timestamp
        self.RA = RA
        self.decl = decl
        self.elongation = elongation
        self.V = V
        self.coordinate = SkyCoord(ra=RA * u.degree, dec=decl * u.degree)

    @classmethod
    def from_dict(cls, d):
        timestamp = datetime(int(d['year']),
                             int(d['month']),
                             int(d['day']),
                             int(d['time'][:2]),
                             int(d['time'][2:]))
        RA = float(d['RA'])
        decl = float(d['decl'])
        elongation = float(d['elong'])
        V = float(d['V'])
        return cls(timestamp, RA, decl, elongation, V)


_field_order = ('year',
                'month',
                'day',
                'time',
                'RA',
                'decl',
                'elong',
                'V',
                "min_min",
                'PA')


class Ephemerides:
    def __init__(self, object_name, ephemerides=None):
        self.object_name = object_name
        if ephemerides is not None:
            self.ephemerides = ephemerides
        else:
            self.ephemerides = []

    def __bool__(self):
        return bool(self.ephemerides)

    def __iter__(self):
        yield from self.ephemerides

    def add(self, ephemeris):
        self.ephemerides.append(ephemeris)

    @property
    def first(self):
        return self.ephemerides[0]

    @property
    def last(self):
        return self.ephemerides[-1]

    @property
    def rest(self):
        return self.ephemerides[1:]

    def span(self, limit=None):
        if limit:
            last = self.ephemerides[limit:][-1]
        else:
            last = self.last

        return self.first.coordinate.separation(last.coordinate)


class EphemeridesSet:
    def __init__(self):
        self.ephemerides_map = {}

    def add(self, ephemerides):
        self.ephemerides_map[ephemerides.object_name] = ephemerides

    def list_objects(self):
        return list(self.ephemerides_map.keys())

    def get(self, object_name):
        return self.ephemerides_map[object_name]

    @classmethod
    def from_minorplanets_tool(cls, s):
        ephemerides_set = cls()

        doc = Document(s)

        for section in doc.sections(start='<p><b>',
                                    end="</pre>",
                                    inclusive=True):
            object_name = section.xpath0('.//b').text
            ephemerides = Ephemerides(object_name)
            pre = section.xpath0('.//pre')
            for line in pre.raw_text.splitlines():
                row = line.split()
                if row and row[0].isnumeric():
                    d = dict(zip(_field_order, row))
                    ephemerides.add(Ephemeris.from_dict(d))
            if ephemerides:
                ephemerides_set.add(ephemerides)

        return ephemerides_set
