import os
from base64 import encodebytes

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import FileSystemBytecodeCache

from . products import ProductList


class JinjaRenderer(object):
    def __init__(self, template_path, extensions=()):
        self.template_path = template_path
        self._loader = FileSystemLoader(template_path)
        self._bytecode_cache = FileSystemBytecodeCache()
        self._environment = Environment(
            loader=self._loader,
            cache_size=-1,
            line_statement_prefix='##',
            extensions=extensions,
            autoescape=True,
            bytecode_cache=self._bytecode_cache)

    def render(self, template_filename, context=None, stream=False):
        if context is None:
            context = {}
        context.update(self.global_context)
        template = self._environment.get_template(template_filename)
        rendered = None
        if stream:
            rendered = template.stream(context)
            rendered.enable_buffering(5)
        else:
            rendered = template.render(context)
        return rendered

    @property
    def global_context(self):
        return dict(_product_list=ProductList())


_site_content_dir = os.path.join(os.path.dirname(__file__),
                                 '../../site_content')
_template_dir = os.path.join(_site_content_dir, 'templates')

renderer = JinjaRenderer(_template_dir)
render = renderer.render


def to_data_uri(b, mimetype):
    encoded_bytes = encodebytes(b).decode()
    encoded_bytes = 'data:{};base64,{}'.format(mimetype, encoded_bytes)
    return encoded_bytes
