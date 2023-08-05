"""
Wextracto uses `Function composition <http://en.wikipedia.org/wiki/Function_composition_%28computer_science%29>`_
as an easy way to build new functions from existing ones:

.. code-block:: pycon

    >>> from wex.composed import compose
    >>> def add1(x):
    ...     return x + 1
    ...
    >>> def mult2(x):
    ...     return x * 2
    ...
    >>> f = compose(add1, mult2)
    >>> f(2)
    6

Wextracto uses the pipe operator, ``|``, as a shorthand for function composition.

This shorthand can be a powerful technique for reducing boilerplate code when
used in combination with :class:`.Attributes`:

.. code-block:: python

    from wex.etree import css, text
    from wex.extractor import Attributes

    attrs = Attributes(
        title = css('h1') | text
        description = css('#description') | text
    )

"""

from itertools import chain


def compose(*functions):
    """ Create a :class:`.ComposedCallable` from zero more functions. """
    return ComposedCallable(*functions)


def composable(func):
    """ Decorates a callable to support function composition using ``|``.

    For example:

    .. code-block:: python

        @Composable.decorate
        def add1(x):
            return x + 1

        def mult2(x):
            return x * 2

        composed = add1 | mult2
    """
    return Composable.decorate(func)


class Composable(object):

    @classmethod
    def decorate(cls, func, **kw):
        name = getattr(func, '__name__', str(func))
        clsdict = dict(
            __call__=staticmethod(func),
            __doc__=getattr(func, '__doc__', None),
            __name__=getattr(func, '__name__', None),
            __module__=getattr(func, '__module__', None),
        )
        clsdict.update(kw)
        return type(name, (cls,), clsdict)()

    @classmethod
    def __getattr__(cls, name):
        return getattr(cls.__call__, name)

    @classmethod
    def __compose__(cls):
        return (cls.__call__,)

    def __or__(self, rhs):
        return compose(self, rhs)

    def __ror__(self, lhs):
        return compose(lhs, self)

    def __call__(self, arg):
        raise NotImplementedError


def flatten(functions):
    iterable = (getattr(f, 'functions', (f,)) for f in functions)
    return tuple(chain.from_iterable(iterable))


class ComposedCallable(Composable):
    """ A callable, taking one argument, composed from other callables.

    .. code-block:: python

        def mult2(x):
            return x * 2

        def add1(x):
            return x + 1

        composed = ComposedCallable(add1, mult2)

        for x in (1, 2, 3):
            assert composed(x) == mult2(add1(x))

    ComposedCallable objects are :func:`composable <wex.composed.composable>`.
    It can be composed of other ComposedCallable objects.  
    """

    def __init__(self, *functions):
        self.functions = flatten(functions)

    def __call__(self, arg, **kw):
        res = arg
        for func in self.functions:
            res = func(res, **kw)
        return res

    def __compose__(self):
        return self.functions

    def __repr__(self):
        return '<%s.%s%r>' % (self.__class__.__module__,
                              self.__class__.__name__,
                              self.functions)


