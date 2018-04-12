# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

#from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.serving import run_simple

from lib.baseapp import BaseApp
from urls import make_url_map


def make_app():
    app = BaseApp(make_url_map)
    return app


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 8080, make_app(), use_reloader=True, use_debugger=True)
else:
    application = make_app()
