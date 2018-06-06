from urllib.request import urlopen
from datetime import datetime

from werkzeug.urls import url_encode
from astropy import units as u
from astropy.coordinates import SkyCoord


class EphemeridesRequest:
    _url = 'https://cgi.minorplanetcenter.net/cgi-bin/confirmeph2.cgi'

    def __init__(self, longitude, latitude, obj, altitude=None, obscode=None):
        self.longitude = longitude
        self.latitude = latitude
        if self.longitude < 0:
            self.longitude += 360

        self.obj = obj
        self.altitude = altitude
        self.obscode = obscode

    def data(self):
        return dict(sort='d',
                    W='j',
                    obj=self.obj,
                    obscode=self.obscode if self.obscode else '',
                    Parallax=2,
                    long=self.longitude,
                    lat=self.latitude,
                    alt=self.altitude if self.altitude is not None else 200,
                    int=2,
                    start=0,
                    raty='d',
                    mot='m',
                    dmot='p',
                    out='f',
                    sun='x',
                    oalt=20)

    def make_request(self):
        s = urlopen(
            self._url, data=url_encode(self.data()).encode('utf8')).read()
        s = s.decode('utf8')
        print(s)
        return Ephemerides.from_minorplanets_tool(s)


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
    def __init__(self, ephemerides):
        self.ephemerides = ephemerides

    def __bool__(self):
        return bool(self.ephemerides)

    def __iter__(self):
        yield from self.ephemerides

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

    @classmethod
    def from_minorplanets_tool(cls, s):
        ephemeris_data = []
        for line in s.split('<pre>')[1].split('</pre>')[0].splitlines():
            data = line.split()
            if data and data[0].isnumeric():
                d = dict(zip(_field_order, data))
                ephemeris_data.append(Ephemeris.from_dict(d))
        return cls(ephemeris_data[:10])
