# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from werkzeug import Response

from lib.render import renderer


def homepage(req):
    return Response(renderer.render('html/landing.html'), mimetype='text/html')