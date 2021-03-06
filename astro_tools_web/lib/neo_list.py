from json import loads
from urllib.request import urlopen

from .encodable import Encodable
from .encodable import decode_list


_json_url = 'https://www.minorplanetcenter.net/Extended_Files/neocp.json'


class NEOCPEntry(Encodable):
    _map = {"Not_Seen_dys": 'not_seen_days',
            "Arc": 'arc',
            "Discovery_day": 'discovery_day',
            "Temp_Desig": "temporary_designation",
            "Decl.": "decl",
            # "Updated": "updated",
            "NObs": 'number_of_observations',
            "V": 'V',
            "Score": 'score',
            "R.A.": 'RA',
            "H": 'H',
            "Discovery_month": 'discovery_month',
            "Discovery_year": 'discovery_year'}

    _table = ('temporary_designation',
              'score',
              'number_of_observations',
              'RA',
              'decl',
              'V',
              'H',
              'arc',
              'not_seen_days')


def get_neos():
    s = urlopen(_json_url).read()
    return decode_list(NEOCPEntry, loads(s))
