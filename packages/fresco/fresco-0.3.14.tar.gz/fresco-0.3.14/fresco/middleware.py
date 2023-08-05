from .util.wsgi import ClosingIterator

import sys
from fresco import context

__all__ = 'FrescoCoreMiddleware', 'XForwarded'


class FrescoCoreMiddleware(object):

    def __init__(self, wsgiapp, frescoapp):
        self.wsgiapp = wsgiapp
        self.frescoapp = frescoapp

    def __call__(self, environ, start_response):

        request = self.frescoapp.request_class(environ)
        context.push(request=request, app=self.frescoapp)
        iterator = self.wsgiapp(environ, start_response)
        try:
            for item in iterator:
                yield item
        except Exception:
            exc_info = sys.exc_info()
            request = context.request
            try:
                response = self.frescoapp.handle_exception(request)
                exc_start_response = lambda s, h, exc_info=exc_info: \
                        start_response(s, h, exc_info)
                for item in response(environ, exc_start_response):
                    yield item
            finally:
                del exc_info
        finally:
            try:
                if self.frescoapp.process_teardown_handlers:
                    self.frescoapp.call_process_teardown_handlers(request)
            finally:
                try:
                    close = getattr(iterator, 'close', None)
                    if close is not None:
                        close()
                finally:
                    context.pop()


class XForwarded(object):
    """\
    Modify the WSGI environment so that the X_FORWARDED_* headers are observed
    and generated URIs are correct in a proxied environment.

    Use this whenever the WSGI application server is sitting behind
    Apache or another proxy server.

    It is easy for clients to spoof the X-Forwarded-For header. You can largely
    protect against this by listing all trusted proxy server addresses in
    ``trusted``. See http://en.wikipedia.org/wiki/X-Forwarded-For for more
    details.

    HTTP_X_FORWARDED_FOR is substituted for REMOTE_ADDR and
    HTTP_X_FORWARDED_HOST for SERVER_NAME. If HTTP_X_FORWARDED_SSL is set, then
    the wsgi.url_scheme is modified to ``https`` and ``HTTPS`` is set to
    ``on``.

    Example::

        >>> from fresco import FrescoApp, context, GET, Response
        >>> from flea import Agent
        >>> app = FrescoApp()
        >>> @app.route('/', GET)
        ... def view():
        ...     return Response(["URL is ", context.request.url,
        ...                      "; REMOTE_ADDR is ",
        ...                      context.request.remote_addr])
        ...
        >>> r = Agent(XForwarded(app))
        >>> response = r.get('/',
        ...     SERVER_NAME='wsgiserver-name',
        ...     SERVER_PORT='8080',
        ...     HTTP_HOST='wsgiserver-name:8080',
        ...     REMOTE_ADDR='127.0.0.1',
        ...     HTTP_X_FORWARDED_HOST='real-name:81',
        ...     HTTP_X_FORWARDED_FOR='1.2.3.4'
        ... )
        >>> response.body
        u'URL is http://real-name:81/; REMOTE_ADDR is 1.2.3.4'
        >>> response = r.get('/',
        ...     SERVER_NAME='wsgiserver-name',
        ...     SERVER_PORT='8080',
        ...     HTTP_HOST='wsgiserver-name:8080',
        ...     REMOTE_ADDR='127.0.0.1',
        ...     HTTP_X_FORWARDED_HOST='real-name:443',
        ...     HTTP_X_FORWARDED_FOR='1.2.3.4',
        ...     HTTP_X_FORWARDED_SSL='on'
        ... )
        >>> response.body
        u'URL is https://real-name/; REMOTE_ADDR is 1.2.3.4'
    """

    def __init__(self, app, trusted=None):
        self.app = app
        if trusted:
            self.trusted = set(trusted)
        else:
            self.trusted = set()

    def __call__(self, environ, start_response):
        """\
        Call the WSGI app, passing it a modified environ
        """
        is_ssl = environ.get('HTTP_X_FORWARDED_SSL') == 'on'

        if 'HTTP_X_FORWARDED_HOST' in environ:
            host = environ['HTTP_X_FORWARDED_HOST']

            if ':' in host:
                port = host.split(':')[1]
            else:
                port = is_ssl and '443' or '80'

            environ['HTTP_HOST'] = host
            environ['SERVER_PORT'] = port

        if is_ssl:
            environ['wsgi.url_scheme'] = 'https'
            environ['HTTPS'] = 'on'

        try:
            forwards = environ['HTTP_X_FORWARDED_FOR'].split(', ')\
                       + [environ.get('REMOTE_ADDR', '')]
        except KeyError:
            # No X-Forwarded-For header?
            return self.app(environ, start_response)

        if self.trusted:
            for ip in forwards[::-1]:
                # Find the first non-trusted ip; this is our remote address
                if ip not in self.trusted:
                    environ['REMOTE_ADDR'] = ip
                    break
        else:
            environ['REMOTE_ADDR'] = forwards[0]

        return self.app(environ, start_response)
