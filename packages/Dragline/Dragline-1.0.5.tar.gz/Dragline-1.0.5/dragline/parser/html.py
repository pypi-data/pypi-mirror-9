from lxml import html, etree
from funcs import xpathstrip, xpathtostring, extract_html, extract_text
from urlparse import urlsplit


ns = etree.FunctionNamespace(None)
ns['strip'] = xpathstrip
ns['str'] = xpathtostring


class HTMLElement(html.HtmlMixin):
    """
    HtmlElement object is returned by the HtmlParser function:

    >>> response = Request('http://www.example.org/').send()
    >>> parser = HtmlParser(response)
    """

    def extract_urls(self, xpath=None, domains=None):
        """
        Returns a list of all the links with given domains
        """
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
        """
        Returns the text content of the element,
        including the text content of its children, with no markup.

        >>> list(parser.extract_urls())
        ['http://www.iana.org/domains/example']
        """

        return extract_text(self)

    def html_content(self):
        return extract_html(self)


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
