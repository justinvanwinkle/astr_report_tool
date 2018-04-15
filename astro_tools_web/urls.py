from werkzeug.routing import Map
from werkzeug.routing import Rule

from endpoint.home import homepage
from endpoint.neo_lookup import neo_lookup

def make_url_map():
    return Map([
        Rule('/', endpoint=homepage, strict_slashes=False),
        Rule('/NEOLookup', endpoint=neo_lookup, strict_slashes=False),
    ])
