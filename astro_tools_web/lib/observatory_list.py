from gzip import decompress
from json import loads
from urllib.request import urlopen

from .encodable import Encodable
from .encodable import decode_dict

_json_url = (
    'http://minorplanetcenter.net/Extended_Files/obscodes_extended.json.gz')


class Observatory(Encodable):
    _map = {"Latitude": 'latitude',
            "Geocentric_dist": 'geocentric_distance',
            "Longitude": 'longitude',
            "Name": "name",
            "cos": 'cos',
            "sin": 'sin'}

    _table = ('code', 'name', 'latitude', 'longitude')


def get_observatories():
    s = decompress(urlopen(_json_url).read())
    return decode_dict(Observatory, loads(s), 'code')
