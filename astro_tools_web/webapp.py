# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from lib.baseapp import BaseApp
from urls import make_url_map


def make_app():
    app = BaseApp(make_url_map)
    return app


if __name__ == '__main__':
    _app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    from werkzeug.serving import run_simple
    run_simple('localhost',
               8080,
               make_app(),
               use_reloader=True,
               use_debugger=True,
               static_files={
                   '/site_content/': os.path.abspath(
                       os.path.join(_app_root, 'site_content')),
                   '/': os.path.abspath(
                       os.path.join(_app_root, 'site_content/static'))})

else:
    application = make_app()
