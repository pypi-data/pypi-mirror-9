python-warouter
===============

Warouter is a simple routing wrapper around webapp2_.


Installing
----------

::

    $ pip install warouter


Usage
-----

Warouter provides url inheritance for handlers and a convenient ``uri_for`` function which can be called with a handler, instead of a string name.

A WSGIApplication mixin is provided which can handle a list of ``url`` decorator handlers.

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


License
-------

MIT


