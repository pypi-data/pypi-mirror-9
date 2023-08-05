"""
Composable functions for extracting data using 
`lxml <http://lxml.de/>`_.
"""

from __future__ import absolute_import, unicode_literals, print_function
import logging
import wex.py2compat ; assert wex.py2compat
from six import string_types
from six.moves.urllib_parse import urljoin, quote, unquote
from functools import partial
from operator import is_, methodcaller
import codecs

from six.moves import reduce

from lxml.etree import XPath, _ElementTree, Element
from lxml.cssselect import CSSSelector
from lxml.html import XHTML_NAMESPACE, HTMLParser

from .composed import composable
from .cache import cached
from .iterable import flatten
from .ncr import replace_invalid_ncr

SKIP = object()
skip = partial(is_, SKIP)

UNPARSEABLE = Element('unparseable')

base_href = XPath('//base[@href]/@href | //x:base[@href]/@href',
                  namespaces={'x': XHTML_NAMESPACE})

space_join = composable(' '.join)


default_namespaces = {'re': 'http://exslt.org/regular-expressions'}


class WrapsShim(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.assignments = {
            '__module__': __name__,
            '__name__': repr(wrapped),
        }

    def __getattr__(self, attr):
        return getattr(self.wrapped, attr, self.assignments[attr])


@composable
@cached
def parse(src):
    """ Returns an element tree create by `LXML <http://lxml.de/>`_. 
       :param src: A readable object such as a :class:`wex.response.Response`.
    """

    if not hasattr(src, 'read'):
        return src
    charset = src.headers.get_content_charset()
    try:
        if charset and codecs.lookup(charset).name == 'iso8859-1':
            charset = 'windows-1252'
    except LookupError:
        pass
    etree = _ElementTree()
    # if charset is not specified in the Content-Type, this will be
    # None ; encoding=None produces default (ISO 8859-1) behavior.
    parser = HTMLParser(encoding=charset)
    try:
        # Sometimes we get URLs containing characters that aren't
        # acceptable to lxml (e.g. "http:/foo.com/bar?this=array[]").
        # When this happens lxml will quote the whole URL.
        # We don't want to have to check for this so we just always
        # quote it here and then unquote it in the `base_url` function.
        quoted_base_url = quote(src.url) if src.url else src.url
        fp = replace_invalid_ncr(src)
        etree.parse(fp, parser=parser, base_url=quoted_base_url)
    except IOError as exc:
        logger = logging.getLogger(__name__)
        logger.warning("IOError parsing %s (%s)", src.url, exc)
    root = etree.getroot()
    if root is None:
        etree._setroot(UNPARSEABLE)
    return etree


@cached
def base_url(root):
    unquoted_base_url = (unquote(root.base_url) if root.base_url
                                                else root.base_url)
    return reduce(urljoin, base_href(root)[:1], unquoted_base_url)


def css(expression):
    """ Returns a :func:`composable <wex.composed.composable>` callable that
        will select elements defined by a 
        `CSS selector <http://en.wikipedia.org/wiki/Cascading_Style_Sheets#Selector>`_ 
        expression.

        :param expression: The CSS selector expression.

        The callable returned accepts a :class:`wex.response.Response`, a
        list of elements or an individual element as an argument.
    """
    return parse | CSSSelector(expression)


def xpath(expression, namespaces=default_namespaces):
    """ Returns :func:`composable <wex.composed.composable>` callable that will
        select elements defined by an 
        `XPath <http://en.wikipedia.org/wiki/XPath>`_ expression.

        :param expression: The XPath expression.
        :param namespaces: The namespaces.

        The callable returned accepts a :class:`wex.response.Response`, a
        list of elements or an individual element as an argument.

        For example:

        .. code-block:: pycon

            >>> from lxml.html import fromstring
            >>> tree = fromstring('<h1>Hello</h1>')
            >>> selector = xpath('//h1')

    """
    return parse | XPath(expression, namespaces=namespaces)


def maybe_list(f):
    #@wraps(WrapsShim(f))
    def wrapper(src, *args, **kwargs):
        cache = {}
        if isinstance(src, list):
            return [ret for ret in (f(i) for i in src) if not skip(ret)]
        return f(src, __maybe_list_cache__=cache)
    return wrapper


def attrib(name, default=SKIP):
    return maybe_list(methodcaller('get', name, default))


def base_url_join(f):
    #@wraps(WrapsShim(f))
    def wrapper(src, *args, **kwargs):
        roottree = src.getroottree() if hasattr(src, 'getroottree') else src
        root = roottree.getroot()
        url = f(src)
        # urljoin requires 'find' so give up if we don't find it (e.g. None)
        if hasattr(url, 'find'):
            return urljoin(base_url(root), url)
        return url
    return wrapper


href = maybe_list(base_url_join(methodcaller('get', 'href', SKIP)))
src = maybe_list(base_url_join(methodcaller('get', 'src', SKIP)))


@composable
def normalize_space(src):
    """ Return a whitespace normalized version of its input.

    :param src: text or iterable.

    If ``src`` is iterable then a generator will be returned.
    """
    if isinstance(src, string_types):
        return space_join(src.split())
    return (normalize_space_and_join(s) for s in src)


@composable
def normalize_space_and_join(src):
    """ Return a string of space-normalized text content. """
    if isinstance(src, string_types):
        return space_join(src.split())
    normalized = [normalize_space_and_join(s) for s in src]
    return space_join((s for s in normalized if s.strip()))


@composable
def itertext(src):
    """ Iterates text from elements.

        :param src: The element or elements to iterate.
    """
    if hasattr(src, 'itertext'):
        # using '*' to exclude comments
        return (t for t in src.itertext('*'))
    elif hasattr(src, '__iter__') and not isinstance(src, string_types):
        return (itertext(s) for s in src)
    return src


#: A :class:`wex.composed.ComposedFunction` that returns the whitespace 
#: normalized text from selected elements.
text = itertext | normalize_space

#: A :class:`wex.composed.ComposedCallable` that yields text nodes.
text_nodes = itertext | flatten

#: A :class:`wex.composed.ComposedFunction` that returns the whitespace 
#: normalized text from zero or more elements joined with a space.
join_text = itertext | normalize_space_and_join
