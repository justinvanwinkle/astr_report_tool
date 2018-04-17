# -*- coding: utf-8 -*-
from werkzeug import Response

from .. lib.render import renderer


def homepage(req):
    ctx = dict(product_name='home')

    return Response(
        renderer.render('html/landing.html',
                        context=ctx),
        mimetype='text/html')
