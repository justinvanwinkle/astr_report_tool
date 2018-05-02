# -*- coding: utf-8 -*-

from urllib.request import urlopen
from werkzeug.urls import url_encode
from astropy import units as u
from astropy.coordinates import SkyCoord

'''
sort=d
W=j
obj=M14TLHe
obj=ZGBE27B
obscode=500
Parallax=1
long=103.0582
lat=38.99085
alt=
int=2
start=0
raty=d
mot=m
dmot=p
out=f
sun=x
oalt=20
'''


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
                    Parallax=1,
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
        return Ephemerides.from_minorplanets_tool(s)


class Ephemeris:

    def __init__(self, timestamp, ra, decl, elongation, V, motion):
        pass


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

    def span(self, limit=None):
        RAs = list(map(float, [float(eph['RA']) for eph in self.ephemerides]))
        decls = list(map(float, [float(eph['decl'])
                                 for eph in self.ephemerides]))

        coords = []
        for RA, decl in zip(RAs, decls):
            coords.append(SkyCoord(ra=RA * u.degree, dec=decl * u.degree))

        if limit:
            coords = coords[:limit]

        sep = coords[0].separation(coords[-1])

        return sep

    @classmethod
    def from_minorplanets_tool(cls, s):
        ephemeris_data = []
        for line in s.split('<pre>')[1].split('</pre>')[0].splitlines():
            data = line.split()
            if data and data[0].isnumeric():
                ephemeris_data.append(dict(zip(_field_order, data)))
        return cls(ephemeris_data[:6])
