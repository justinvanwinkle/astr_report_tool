from urllib.parse import urljoin
import re
from json import loads

import lxml.etree as ET
from html5_parser import parse
from werkzeug import cached_property

_charset_re = re.compile(r'charset=([^;]+)')
_text_split_re = re.compile(r'>\s?([^<]+?)\s?<')


def condense_whitespace(s):
    return ' '.join(s.split())


class RExtractor(object):

    def __init__(self, doc, template=None):
        self.doc = doc
        self.template = template

    def ex(self, *args, **kw):
        ex_re = re.compile(self.template % (args or kw),
                           re.DOTALL)

        m = ex_re.search(self.doc.html)
        if m:
            return m.groups()[0]


class Document(object):

    def __init__(self, html=None, tree=None):
        """ Initialize a Document instance.

        - html: Give a str or unicode object containing html
            or xml, a parsed version of which we can access via
            the tree and xml attributes respectively.  This should
            be specified as a unicode object when possible, if a string
            is passed, an attempt will be made to parse it as utf-8.
            If that fails, an expensive call is made to analyze the
            text to determine a reasonable guess as to its encoding.

         - tree: An ElementTree tree.  A unicode representation of the text is
            made available via the html element.  """

        if html is not None:
            self.set_html(html)
        elif tree is not None:
            self.tree = tree

    def set_html(self, html, charset=None):
        try:
            self.html = html
        except UnicodeDecodeError:
            pass

    @cached_property
    def html(self):
        # encoding and then decoding is ugly, but it's all we have until
        #  somebody figures out how to get the html5lib serializer working
        #  with elementtree
        return ET.tostring(self.tree, encoding='utf-8').decode('utf-8')

    def filedump(self, fn=None):
        """ Writes the html to a file. For debugging purposes. """
        fn = fn or "scrape%s.html" % hash(self)
        f = open(fn, 'w')
        f.write(self.html)
        f.close()
        return fn

    def attr(self, name, default=None):
        return self.tree.attrib.get(name, default)

    def itertext(self):
        for el in self.tree.iter():
            text = ''
            if el.text is not None and isinstance(el.tag, str):
                text += el.text
            if el.tail is not None:
                text += el.tail
            yield text

    # Don't cache raw_text, it probably will very rarely be used, if ever.
    @property
    def raw_text(self):
        return ''.join(self.itertext())

    @property
    def text(self):
        return condense_whitespace(self.raw_text)

    @cached_property
    def tail(self):
        return self.tree.tail

    @cached_property
    def xml(self):
        return ET.fromstring(self.html)

    @cached_property
    def json(self):
        return loads(self.html)

    @cached_property
    def tree(self):
        tree = parse(self.html)
        return tree

    def make_links_absolute(self, base_url=None):
        for tag, attr in [('img', 'src'),
                          ('a', 'href'),
                          ('form', 'action'),
                          ('link', 'href'),
                          ('script', 'src')]:
            for el in self.tree.findall('.//%s' % tag):
                if el.attrib.get(attr):
                    el.attrib[attr] = urljoin(base_url, el.attrib[attr])

    def _xpath(self, selector):
        return self.tree.findall(selector)

    def _xpath0(self, selector):
        return self.tree.find(selector)

    def xpath(self, selector):
        return self.sections(xpath=selector)

    def xpath0(self, selector):
        return self.section(xpath=selector)

    def sections(self,
                 start=None,
                 end=None,
                 inclusive=False,
                 section_re=None,
                 xpath=None,
                 first=False,
                 klass=None):
        """ Returns subsections of document.

        Arguments:
          start: regex representing the beginning of each section
          end: regex representing the end of each section

          split_re: regex which captures each section
          selector: xpath selector for each element to selector

          you must specify start and end, or one of the others
          #TODO: test
        """
        assert bool(start and end) + bool(xpath) + bool(section_re) == 1, \
            "Undefined combination of arguments given"

        if not klass:
            klass = Document

        if start and end:
            if inclusive:
                section_re = re.compile(r'(%s.+?%s)' % (start, end), re.DOTALL)
            else:
                section_re = re.compile(r'%s(.+?)%s' % (start, end), re.DOTALL)

        if section_re:
            if not hasattr(section_re, 'match'):
                section_re = re.compile(section_re)
            return [klass(html=x) for x
                    in section_re.findall(self.html)]

        if xpath:
            if first:
                el = self._xpath0(xpath)
                if el is not None:
                    return klass(tree=el)
                return None
            else:
                els = self._xpath(xpath)
                return [klass(tree=x) for x in els]

    def section(self, *args, **kw):
        return self.sections(*args, first=True, **kw)

    def section_matching(self, match, *args, **kw):
        sections = self.sections(*args, **kw)
        for section in sections:
            m = section.search(match)
            if m:
                return section

    def sections_matching(self, match, *args, **kw):
        matching_sections = []
        sections = self.sections(*args, **kw)
        for section in sections:
            m = section.search(match)
            if m:
                matching_sections.append(section)

        return matching_sections

    def search(self, regex):
        if not hasattr(regex, 'search'):
            regex = re.compile(regex, re.DOTALL)

        return regex.search(self.html)

    def findall(self, regex):
        """ Perform a regular expression lookup inside the html of the
        document.

        regex: either a string to be compiled into a regex,
                or an object (such as an re instance) that implements
                .findall(unicode_str).
        """
        if not hasattr(regex, 'findall'):
            regex = re.compile(regex, re.DOTALL)

        return regex.findall(self.html)

    def text_split(self):
        """ Return the text nodes as a list of strings. """
        return list(self.itertext())

    def normalized_text_split(self):
        "Return the text nodes as a list of whitespaced normalized strings."
        return list(' '.join(t.split()) for t in self.itertext() if t.strip())
