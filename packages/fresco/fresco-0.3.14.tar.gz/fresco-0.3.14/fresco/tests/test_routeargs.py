from __future__ import absolute_import

from mock import Mock

from fresco import Route, GET, FrescoApp, Response
from fresco import routeargs


class TestRouteArg(object):

    def test_routekwarg_configured(self):

        A = routeargs.RouteArg()
        route = Route('/', GET, lambda r: None, x=A)
        assert A.route is route
        assert A.name is 'x'

    def test_routekwarg_value_passed(self):

        view = Mock(return_value=Response())
        routekwarg = Mock(spec=routeargs.RouteArg)
        routekwarg.return_value = 'xyzzy'

        app = FrescoApp()
        app.route('/', GET, view, x=routekwarg)
        with app.requestcontext('/') as c:
            app.view()
            routekwarg.assert_called_with(c.request)
            view.assert_called_with(x='xyzzy')

    def test_queryarg_value_passed(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.QueryArg())
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_formarg_value_passed(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg())
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_sessionarg_value_passed(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.SessionArg())
        with app.requestcontext('/?x=foo') as c:
            c.request.environ[c.request.SESSION_ENV_KEY] = {'x': 'foo'}
            app.view()
            view.assert_called_with(x='foo')

    def test_cookiearg_value_passed(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.CookieArg())
        with app.requestcontext('/', HTTP_COOKIE='x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_cookiearg_listvalue_passed(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.CookieArg([str]))
        with app.requestcontext('/', HTTP_COOKIE='x=foo;x=bar'):
            app.view()
            view.assert_called_with(x=['foo', 'bar'])

    def test_requestarg_value_converted(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg(float))
        with app.requestcontext('/?x=0'):
            app.view()
            view.assert_called_with(x=0.0)

    def test_requestarg_default_value(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg(default='d'))
        with app.requestcontext('/'):
            app.view()
            view.assert_called_with(x='d')

    def test_it_doesnt_convert_default_values(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg(int, default=None))
        with app.requestcontext('/'):
            app.view()
            view.assert_called_with(x=None)

    def test_access_to_missing_requestarg_returns_badrequest(self):
        def view(x):
            x == 0
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg())
        with app.requestcontext('/'):
            assert 'Bad Request' in app.view().status

    def test_missing_requestarg_with_conversion_returns_badrequest(self):
        def view(x):
            x == 0
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg(int))
        with app.requestcontext('/'):
            assert 'Bad Request' in app.view().status

    def test_routeargs_work_as_positional_arguments(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, args=[routeargs.FormArg(key='x')])
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with('foo')

    def test_routearg_classes_are_auto_instantiated(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg)
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with(x='foo')


class TestRequestObject(object):

    def test_it_passes_the_request(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.RequestObject())
        with app.requestcontext('/') as c:
            app.view()
            x = view.call_args[1]['x']
            assert x is c.request


class Test_routearg(object):

    def test_it_calls_func(object):

        view = Mock(return_value=Response())
        argfunc = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.routearg(argfunc))
        with app.requestcontext('/'):
            app.view()
            assert argfunc.call_count == 1, argfunc.call_count
            assert view.call_args[1]['x'] is argfunc()

    def test_it_passes_additional_args(object):

        view = Mock(return_value=Response())
        argfunc = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.routearg(argfunc, 'x', y=42))
        with app.requestcontext('/') as c:
            app.view()
            assert argfunc.call_args == ((c.request, 'x'), {'y': 42})
            assert view.call_args[1]['x'] is argfunc()


class TestFormData(object):

    def test_it_passes_the_form_dict(self):
        view = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormData())
        with app.requestcontext('/') as c:
            app.view()
            x = view.call_args[1]['x']
            assert x is c.request.form
