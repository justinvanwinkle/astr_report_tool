from werkzeug.routing import Map
from werkzeug.routing import Rule


def make_url_map():
    # import inside this function to make imports lazy
    #   so syntax errors don't crash the development server
    from .endpoint.home import homepage
    from .endpoint.neo_lookup import neo_lookup
    from .endpoint.neo_lookup import ajax_object_track
    from .endpoint.neo_lookup import object_list

    return Map([
        Rule('/', endpoint=homepage, strict_slashes=False),
        Rule('/NEOLookup', endpoint=neo_lookup, strict_slashes=False),
        Rule('/ajax_object_track', endpoint=ajax_object_track),
        Rule('/object_list', endpoint=object_list)
    ])
