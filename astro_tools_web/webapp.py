# -*- coding: utf-8 -*-

from os.path import abspath
from os.path import dirname
from os.path import join


def make_app():
    from astro_tools_web.lib.baseapp import BaseApp
    from astro_tools_web.urls import make_url_map

    app = BaseApp(make_url_map)
    return app


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    _app_root = abspath(join(dirname(__file__), '../'))

    run_simple('localhost',
               8080,
               make_app(),
               use_reloader=True,
               use_debugger=True,
               static_files={
                   '/site_content/': abspath(
                       join(_app_root, 'site_content')),
                   '/': abspath(
                       join(_app_root, 'site_content/static'))})

else:
    application = make_app()
