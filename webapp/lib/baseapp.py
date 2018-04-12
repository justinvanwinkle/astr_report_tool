# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from werkzeug import Request
from werkzeug import cached_property


class BaseApp(object):
    def __init__(self, url_map_maker):
        self._url_map_maker = url_map_maker

    def __call__(self, environ, start_response):
        urls = self.url_map.bind_to_environ(environ)
        endpoint, args = urls.match()
        request = Request(environ)
        args['req'] = request

        response = endpoint(**args)
        return response(environ, start_response)

    @cached_property
    def url_map(self):
        return self._url_map_maker()
