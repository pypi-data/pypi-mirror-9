# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
"""\
Utilities for interfacing with WSGI
"""

from __future__ import absolute_import

from functools import partial
from io import BytesIO
import sys

from fresco.compat import unquote, urlparse

__all__ = ['environ_to_unicode',
           'unicode_to_environ',
           'environ_to_bytes',
           'bytes_to_environ',
           'StartResponseWrapper',
           'ClosingIterator',
           'make_environ',
           ]


#: The core keys expected in the WSGI environ dict, as defined by PEP3333
WSGI_KEYS = set(['REQUEST_METHOD',
                 'SCRIPT_NAME',
                 'PATH_INFO',
                 'QUERY_STRING',
                 'CONTENT_TYPE',
                 'CONTENT_LENGTH',
                 'SERVER_NAME',
                 'SERVER_PORT',
                 'SERVER_PROTOCOL'])


def with_docstring_from(src):
    def with_docstring_from(tgt):
        try:
            tgt.__doc__ = src.__doc__
        except AttributeError:
            tgt.func_doc = src.func_doc
        return tgt
    return with_docstring_from


def _environ_to_unicode_py2(s, enc='UTF-8'):
    """
    Decode a WSGI environ value to a unicode string
    """
    return s.decode(enc)


@with_docstring_from(_environ_to_unicode_py2)
def _environ_to_unicode_py3(s, enc='UTF-8'):
    return s.encode('iso-8859-1').decode(enc)


def _unicode_to_environ_py2(s, enc='UTF-8'):
    """
    Return a unicode string encoded for a WSGI environ value

    For python 2, this simply returns ``s`` encoded using the specified
    encoding

    For python 3 this returns a 'bytes-as-unicode' string:

    - encode ``s`` using the specified encoding (eg utf8)
    - decode the resulting byte string as latin-1
    """
    return s.encode(enc, 'surrogateescape')


@with_docstring_from(_unicode_to_environ_py2)
def _unicode_to_environ_py3(s, enc='UTF-8'):
    return s.encode(enc, 'surrogateescape').decode('iso-8859-1')


def _environ_to_bytes_py2(s):
    """
    Decode a WSGI environ value to a bytes object
    """
    return s


@with_docstring_from(_environ_to_bytes_py2)
def _environ_to_bytes_py3(s):
    return s.encode('latin1')


def _bytes_to_environ_py2(s):
    """
    Encode a byte string to a WSGI environ value

    For Python 2, this simply returns ``s``.
    For Python 3 this returns a 'bytes-as-unicode' string.
    """
    return s


@with_docstring_from(_environ_to_bytes_py2)
def _bytes_to_environ_py3(s):
    return s.decode('latin1')


if str is bytes:
    environ_to_unicode = _environ_to_unicode_py2
    unicode_to_environ = _unicode_to_environ_py2
    environ_to_bytes = _environ_to_bytes_py2
    bytes_to_environ = _bytes_to_environ_py2

else:
    environ_to_unicode = _environ_to_unicode_py3
    unicode_to_environ = _unicode_to_environ_py3
    environ_to_bytes = _environ_to_bytes_py3
    bytes_to_environ = _bytes_to_environ_py3


class StartResponseWrapper(object):
    """\
    Wrapper class for the ``start_response`` callable, allowing middleware
    applications to intercept and interrogate the proxied start_response
    arguments.

    Synopsis::

        >>> def my_wsgi_app(environ, start_response):
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ['Whoa nelly!']
        ...
        >>> def my_other_wsgi_app(environ, start_response):
        ...     responder = StartResponseWrapper(start_response)
        ...     result = my_wsgi_app(environ, responder)
        ...     print "Got status", responder.status
        ...     print "Got headers", responder.headers
        ...     responder.call_start_response()
        ...     return result
        ...
        >>> from flea import Agent
        >>> result = Agent(my_other_wsgi_app).get('/')
        Got status 200 OK
        Got headers [('Content-Type', 'text/plain')]

    See also ``Response.from_wsgi``, which takes a wsgi callable, environ and
    start_response, and returns a ``Response`` object, allowing the client to
    further interrogate and customize the WSGI response.

    Note that it is usually not advised to use this directly in middleware as
    start_response may not be called directly from the WSGI application, but
    rather from the iterator it returns. In this case the middleware may need
    logic to accommodate this. It is usually safer to use
    ``Response.from_wsgi``, which takes this into account.
    """

    def __init__(self, start_response):
        self.start_response = start_response
        self.status = None
        self.headers = []
        self.called = False
        self.buf = BytesIO()
        self.exc_info = None

    def __call__(self, status, headers, exc_info=None):
        """
        Dummy WSGI ``start_response`` function that stores the arguments for
        later use.
        """
        self.status = status
        self.headers = headers
        self.exc_info = exc_info
        self.called = True
        return self.buf.write

    def call_start_response(self):
        """
        Invoke the wrapped WSGI ``start_response`` function.
        """
        try:
            write = self.start_response(
                self.status,
                self.headers,
                self.exc_info
            )
            write(self.buf.getvalue())
            return write
        finally:
            # Avoid dangling circular ref
            self.exc_info = None


class ClosingIterator(object):
    """\
    Wrap a WSGI iterator to allow additional close functions to be called on
    application exit.

    Synopsis::

        >>> class filelikeobject(object):
        ...
        ...     def read(self):
        ...         print "file read!"
        ...         return ''
        ...
        ...     def close(self):
        ...         print "file closed!"
        ...
        >>> def app(environ, start_response):
        ...     f = filelikeobject()
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ClosingIterator(iter(f.read, ''), f.close)
        ...
        >>> from flea import Agent
        >>> m = Agent(app).get('/')
        file read!
        file closed!

    """

    def __init__(self, iterable, *close_funcs):
        """
        Initialize a ``ClosingIterator`` to wrap iterable ``iterable``, and
        call any functions listed in ``*close_funcs`` on the instance's
        ``.close`` method.
        """
        self.__dict__['_iterable'] = iterable
        self.__dict__['_next'] = partial(next, iter(self._iterable))
        self.__dict__['_close_funcs'] = close_funcs
        iterable_close = getattr(self._iterable, 'close', None)
        if iterable_close is not None:
            self.__dict__['_close_funcs'] = (iterable_close,) + close_funcs
        self.__dict__['_closed'] = False

    def __iter__(self):
        """
        ``__iter__`` method
        """
        return self

    def __next__(self):
        """\
        Return the next item from the iterator
        """
        return self._next()

    def next(self):
        """
        Return the next item from ``iterator``
        """
        return self._next()

    def close(self):
        """
        Call all close functions listed in ``*close_funcs``.
        """
        self.__dict__['_closed'] = True
        for func in self._close_funcs:
            func()

    def __getattr__(self, attr):
        return getattr(self._iterable, attr)

    def __setattr__(self, attr, value):
        return getattr(self._iterable, attr, value)

    def __del__(self):
        """
        Emit a warning if the iterator is deleted without ``close`` having been
        called.
        """
        if not self._closed:
            try:
                import warnings
            except ImportError:
                return
            else:
                warnings.warn("%r deleted without close being called" %
                              (self,))


class WSGIStack(object):
    """
    A context manager that sets up a WSGI request environ
    passed through a list of middleware.
    """

    def __init__(self, environ, middleware_stack):
        self.environ = environ
        self.middleware_stack = middleware_stack
        app = self.fake_app
        for m in middleware_stack:
            app = m(app)
        self.app = app
        self.content_iterator = self.app(environ, lambda *a, **kw: None)

    def fake_app(self, environ, start_response):
        start_response('200 OK', [])
        yield b''

    def __enter__(self):
        # Invoke the fake WSGI app. This executes any middleware, which may
        # have side effects required downstream (eg setting environ keys)
        next(self.content_iterator, None)
        return self.environ

    def __exit__(self, type, value, traceback):
        # Exhaust the iterator and close up
        list(self.content_iterator)
        getattr(self.content_iterator, 'close', lambda: None)()


def make_environ(url='/', environ=None,
                    wsgi_input=b'', middleware=True, **kwargs):
    """
    Return a WSGI environ dict populated with values modelling the specified
    request url and data.

    :param url: The URL for the request,
                eg ``/index.html`` or ``/search?q=foo``.
                Note that ``url`` must be properly URL encoded.
    :param environ: values to pass into the WSGI environ dict
    :param wsgi_input: The input stream to use in the ``wsgi.input``
                        key of the environ dict
    :param middleware: If ``False`` the middleware stack will not be
                        invoked. Disabling the middleware can speed up
                        the execution considerably, but it will no longer
                        give an accurate simulation of a real HTTP request.
    :param kwargs: additional keyword arguments will be passed into the
                    WSGI request environment
    """
    from fresco.request import HEADER_NAMES as REQUEST_HEADER_NAMES
    url = urlparse(url)
    netloc = url.netloc
    user = ''
    if '@' in netloc:
        user, netloc = netloc.split('@', 1)

    if ':' in user:
        user, _ = user.split(':')[0]

    if isinstance(wsgi_input, bytes):
        wsgi_input = BytesIO(wsgi_input)

    env_overrides = environ or {}
    for key, value in kwargs.items():
        key = key.replace('wsgi_', 'wsgi.')
        if '.' not in key:
            # Convert core WSGI keys to upper case
            if key.upper() in WSGI_KEYS:
                key = key.upper()
            # Convert header names to form HTTP_USER_AGENT
            elif key.lower() in REQUEST_HEADER_NAMES:
                key = 'HTTP_' + key.upper()
            # value must be a python native str, whatever that means
            if not isinstance(value, str):
                value = unicode_to_environ(value)
        env_overrides[key] = value

    environ = {
        'REQUEST_METHOD': 'GET',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.0',
        'HTTP_HOST': netloc or 'localhost',
        'SCRIPT_NAME': '',
        'PATH_INFO': unicode_to_environ(unquote(url.path)),
        'REMOTE_ADDR': '127.0.0.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': url.scheme or 'http',
        'wsgi.input': wsgi_input,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    if url.scheme == 'https':
        environ['HTTPS'] = 'on'
        environ['SERVER_PORT'] = '443'

    if user:
        environ['REMOTE_USER'] = user

    if url.query:
        environ['QUERY_STRING'] = url.query

    environ.update(env_overrides)
    return environ
