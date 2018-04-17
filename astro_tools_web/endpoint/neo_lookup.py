# -*- coding: utf-8 -*-
from werkzeug import Response

from lib.render import renderer
from lib.neo_list import get_neos
from lib.neo_list import NEOCPEntry
from lib.observatory_list import Observatory
from lib.observatory_list import get_observatories


def neo_lookup(req):
    ctx = dict(product_name='neo_lookup')
    ctx['neos'] = get_neos()
    ctx['NEOCPEntry'] = NEOCPEntry

    ctx['Observatory'] = Observatory
    ctx['observatories'] = get_observatories()

    return Response(
        renderer.render('html/neo_lookup.html',
                        context=ctx),
        mimetype='text/html')
