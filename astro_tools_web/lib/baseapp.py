from werkzeug import Request
from werkzeug import Response
from werkzeug import cached_property
from werkzeug.exceptions import NotFound


class BaseApp(object):
    def __init__(self, url_map_maker):
        self._url_map_maker = url_map_maker

    def __call__(self, environ, start_response):
        urls = self.url_map.bind_to_environ(environ)

        try:
            endpoint, args = urls.match()
            request = Request(environ)
            args['req'] = request
            response = endpoint(**args)
        except NotFound:
            # kill tracebacks if browser is looking for js map files
            if environ['PATH_INFO'].endswith('.js.map'):
                response = Response('', status=404)
            else:
                raise

        return response(environ, start_response)

    @cached_property
    def url_map(self):
        return self._url_map_maker()
