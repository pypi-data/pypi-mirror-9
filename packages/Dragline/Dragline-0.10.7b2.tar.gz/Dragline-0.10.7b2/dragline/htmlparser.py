from lxml import html, etree
from parslepy import Parselet
from parslepy.funcs import xpathstrip, xpathtostring
from cssselect import HTMLTranslator
import re
from urlparse import urlsplit


ns = etree.FunctionNamespace(None)
ns['strip'] = xpathstrip
ns['str'] = xpathtostring


class HTMLElement(html.HtmlMixin):

    def extract_urls(self, xpath=None, domains=None):
        if xpath and not xpath.endswith('/'):
            xpath += '/'
        elif xpath is None:
            xpath = ""
        for url in map(urlsplit, set(self.xpath(xpath + "descendant-or-self::a/@href"))):
            if url.scheme in ['http', 'https'] and url.hostname:
                if domains and url.hostname not in domains:
                    continue
                yield url.geturl()

    def extract_text(self):
        return "".join(i.strip() for i in self.itertext())

    def css(self, expr):
        return self.xpath(self.cssselect(expr))

    def html_content(self, pretty_print=False):
        return html.tostring(self, pretty_print, encoding=unicode)


class HtmlComment(etree.CommentBase, HTMLElement):
    pass


class HtmlElement(etree.ElementBase, HTMLElement):
    pass


class HtmlProcessingInstruction(etree.PIBase, HTMLElement):
    pass


class HtmlEntity(etree.EntityBase, HTMLElement):
    pass


class HtmlElementClassLookup(html.HtmlElementClassLookup):

    def lookup(self, node_type, document, namespace, name):
        if node_type == 'element':
            return self._element_classes.get(name.lower(), HtmlElement)
        elif node_type == 'comment':
            return HtmlComment
        elif node_type == 'PI':
            return HtmlProcessingInstruction
        elif node_type == 'entity':
            return HtmlEntity
        # Otherwise normal lookup
        return None


class HTMLParser(etree.HTMLParser):

    """An HTML parser that is configured to return lxml.html Element
    objects.
    """

    def __init__(self, **kwargs):
        super(HTMLParser, self).__init__(**kwargs)
        self.set_element_class_lookup(HtmlElementClassLookup())


def HtmlParser(response, absolute_links=True):
    """
    :param response:
    :type response: :class:`dragline.http.Response`

    This method takes response object as its argument and returns
    the lxml etree object.

    HtmlParser function returns a lxml object of type HtmlElement which got few potential methods.
    All the details of lxml object are discussed in section `lxml.html.HtmlElement`.
    """
    encoding = response.encoding if hasattr(response, 'encoding') else 'utf-8'
    parser = HTMLParser(recover=True, encoding=encoding)
    if isinstance(response, basestring):
        element = html.fromstring(response, None, parser)
    else:
        element = html.fromstring(response.content, response.url, parser)
        if absolute_links:
            element.make_links_absolute()
    return element
