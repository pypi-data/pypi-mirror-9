# -*- encoding: utf-8 -*-
"""
Warouter is a simple routing wrapper around webapp2_.

It provides url inheritance for handlers and a convenient
:func:`uri_for` function which can be called with a handler, instead of
a string name.

A WSGIApplication mixin is provided which can handle a list of
:func:`url` decorator handlers.

Example:

>>> import warouter
>>> import webapp2
>>>
>>> @warouter.url('/')
... class RootHandler(webapp2.RequestHandler):
...     def get(self):
...         self.response.write('root')
...
>>> @warouter.url('/child/<child_param:([a-z]+)>')
... class ChildHandler(RootHandler):
...     def get(self, child_param):
...         self.response.write(child_param)
...     def put(self, child_param):
...         pass
...
>>> @warouter.url('/grandchild/<grandchild_param:([a-z]+)>')
... class GrandChildHandler(ChildHandler):
...     def get(self, child_param, grandchild_param):
...         self.response.write('\n'.join([child_param, grandchild_param]))
...     def post(self, child_param, grandchild_param):
...         self.response.write(warouter.uri_for(ChildHandler,
...                                              child_param=child_param))
...
>>> assert RootHandler.url == '/'
>>> assert ChildHandler.url == '/child/<child_param:([a-z]+)>'
>>> assert GrandChildHandler.url == (
...     '/child/<child_param:([a-z]+)>/grandchild/<grandchild_param:([a-z]+)>')
>>> assert GrandChildHandler.put is None
>>>
>>> app = warouter.WSGIApplication([
...     RootHandler,
...     ChildHandler,
...     GrandChildHandler
... ])
>>>
>>> if __name__ == '__main__':
...     from paste import httpserver
...     httpserver.serve(app, port='8080')
...
>>>

The above example requires Paste_, which can be installed using::

    $ pip install paste


.. _Paste: https://pypi.python.org/pypi/Paste
.. _webapp2: https://webapp-improved.appspot.com/

"""
from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import logging
import pydoc

import webapp2


_handlers = set()


def url(url, **param_mapping):
    """
    Specifies a url for a :class:`webapp2.RequestHandler`.

    This decorator specifies a url for a handler by appending it to the
    url of its parent handlers.

    A param mapping may be specified as keyword arguments. the url
    parameters will be matched against these values and be converted by
    the callable specified as the kwarg value.

    Args:
        url (basestring): The url to append to the decorated handler.
        **param_mapping: A dict of key, value pairs where the key
            specifies the name of a url parameter to vonvert and the
            value a callable used to convert the url parameter.

    """
    def inner(handler):
        handler._appended_url = url
        if param_mapping:
            if hasattr(handler, '_param_mapping'):
                handler._param_mapping = handler._param_mapping.copy()
                handler._param_mapping.update(param_mapping)
            else:
                handler._param_mapping = param_mapping.copy()

        def fn_wrapper(fn):
            @functools.wraps(fn)
            def fn_inner(*args, **kwargs):
                if hasattr(handler, '_param_mapping'):
                    for key, value in kwargs.iteritems():
                        if key in handler._param_mapping:
                            kwargs[key] = handler._param_mapping[key](value)
                return fn(*args, **kwargs)

            return fn_inner

        full_url = ''
        for base in reversed(handler.mro()):
            try:
                if base._appended_url != '/':
                    full_url += base._appended_url
                elif base is handler:
                    full_url = base._appended_url
                    break
            except AttributeError:
                pass
            for method in webapp2.WSGIApplication.allowed_methods:
                method = method.lower()
                if base is handler:
                    break
                try:
                    if(getattr(base, method).im_func is
                       getattr(handler, method).im_func):
                        setattr(handler, method, None)
                except AttributeError:
                    pass

        for method in webapp2.WSGIApplication.allowed_methods:
            method = method.lower()
            try:
                setattr(handler, method, fn_wrapper(getattr(handler, method)))
            except AttributeError:
                pass
        _handlers.add(handler)
        handler.url = full_url
        return handler
    return inner


class WSGIApplicationMixin(object):
    """
    This mixin allows a list of :func:`url` decorated request handlers
    to be passed to the WSGI application mapping instead of
    :class:`webapp2.Route` objects or tuples.

    """
    #: The logger to use when logging. May be overridden by subclasses.
    warouter_logger = logging
    #: logging level at which to log the handler mapping. May be
    #: overridden by subclasses.
    warouter_logging_level = logging.NOTSET
    #: String format to log. fill be formatted with the url and handler.
    #: May be overridden by subclasses.
    warouter_logging_format = '{0} → {1.__module__}.{1.__name__}'

    def __init__(self, mapping, *args, **kwargs):
        processed = []
        for m in mapping:
            if m in _handlers:
                self.warouter_logger.log(
                    self.warouter_logging_level,
                    self.warouter_logging_format.format(m.url, m))
                processed.append(webapp2.Route(m.url, m, name=m.url))
            else:
                processed.append(m)
        super(WSGIApplicationMixin, self).__init__(processed, *args, **kwargs)


class WSGIApplication(WSGIApplicationMixin, webapp2.WSGIApplication):
    """
    Implements :class:`WSGIApplicationMixin` and
    :class:`webapp2.WSGIApplication` for convenience.

    """


def uri_for(handler, *args, **kwargs):
    """
    Gets the uri for a handler based on its url.

    Args:
        handler (webapp2.RequestHandler): The handler for which to find a url.
            If this is a string, it will be tried to import a handler
            from this string.
        args: passed to :func:`webapp2.uri_for`.
        kwargs: passed to :func:`webapp2.uri_for`.

    Returns:
        basestring: A string containing the url for the handler.

    """
    if isinstance(handler, basestring):
        handler = pydoc.locate(handler)
    return webapp2.uri_for(handler.url, *args, **kwargs)
