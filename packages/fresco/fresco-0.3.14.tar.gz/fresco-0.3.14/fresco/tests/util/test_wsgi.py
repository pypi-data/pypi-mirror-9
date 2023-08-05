from __future__ import absolute_import

from fresco import FrescoApp, Response
from fresco.util.wsgi import ClosingIterator, StartResponseWrapper


class Counter(object):

    value = 0

    def inc(self):
        self.value += 1


def start_response(status, headers, exc_info=None):
    pass


class _TestException(Exception):
    pass


class TestClosingIterator(object):

    def app(self, environ, start_response):
        start_response('200 OK', [('Content-Type: text/plain')])
        yield "Foo"
        yield "Bar"

    def test_close_called_after_iterator_finished(self):
        count = Counter()
        environ = {}

        result = self.app(environ, start_response)
        result = ClosingIterator(result, count.inc)
        assert count.value == 0
        try:
            list(result)
        finally:
            result.close()
        assert count.value == 1

    def test_multiple_close_functions_called(self):
        count1 = Counter()
        count2 = Counter()
        environ = {}

        result = self.app(environ, start_response)
        result = ClosingIterator(result, count1.inc, count2.inc)
        assert count1.value == 0
        assert count2.value == 0
        try:
            list(result)
        finally:
            result.close()
        assert count1.value == 1
        assert count2.value == 1


class TestStartResponseWrapper(object):

    def test_write(self):

        def wsgiapp(environ, start_response):
            start_response = StartResponseWrapper(start_response)
            write = start_response('200 OK', [('Content-Type', 'text/plain')])

            write(b'cat')
            write(b'sat')
            write2 = start_response.call_start_response()
            write2(b'mat')
            return []

        with FrescoApp().requestcontext() as c:
            r = Response.from_wsgi(wsgiapp,
                                   c.request.environ,
                                   lambda status, headers: None)
            assert b''.join(r.content) == b'catsatmat'
