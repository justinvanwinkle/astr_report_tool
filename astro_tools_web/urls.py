from werkzeug.routing import Map
from werkzeug.routing import Rule


def make_url_map():
    # import inside this function to make imports lazy
    #   so syntax errors don't crash the development server
    from .endpoint.home import homepage
    from .endpoint.neo_lookup import neo_lookup
    from .endpoint.neo_lookup import neo_ephemerides
    from .endpoint.neo_lookup import object_track

    return Map([
        Rule('/', endpoint=homepage, strict_slashes=False),
        Rule('/NEOLookup', endpoint=neo_lookup, strict_slashes=False),
        Rule('/neo_ephemerides', endpoint=neo_ephemerides),
        Rule('/neo_object_track', endpoint=object_track)
    ])
