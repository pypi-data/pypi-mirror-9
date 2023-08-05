# encoding: utf-8
from __future__ import absolute_import

from copy import copy
from functools import wraps

from mock import Mock
import pytest
import tms

from fresco import FrescoApp, ALL_METHODS, GET, POST, Response
from fresco.exceptions import NotFound
from fresco.compat import ustr
from fresco.core import urlfor
from fresco.routing import (
    Route, DelegateRoute, RouteCollection, routefor, RouteTraversal,
    RouteNotFound)
from . import fixtures


def assert_method_bound_to(method, ob):
    try:
        assert method.__self__ is ob
    except AttributeError:
        assert method.im_self is ob


class TestMethodDispatch(object):

    def test_route_is_dispatched_to_correct_method(self):

        getview = Mock(return_value=Response())
        postview = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, getview)
        app.route('/', POST, postview)

        with app.requestcontext('/'):
            app.view()
            assert getview.call_count == 1
            assert postview.call_count == 0

        with app.requestcontext_post('/'):
            app.view()
            assert getview.call_count == 1
            assert postview.call_count == 1


class TestRouteConstructor(object):

    def test_multiple_views_can_be_associated_with_a_route(self):

        app = FrescoApp()
        v1 = Mock(return_value=Response())
        v2 = Mock(return_value=Response())
        app.route('/', GET=v1, POST=v2)

        with app.requestcontext():
            app.view()
            assert v1.call_count == 1
            assert v2.call_count == 0

        with app.requestcontext_post():
            app.view()
            assert v1.call_count == 1
            assert v2.call_count == 1

    def test_kwargs_take_precedence(self):
        app = FrescoApp()
        v1 = Mock(return_value=Response())
        v2 = Mock(return_value=Response())
        app.route('/', ALL_METHODS, v1, POST=v2)

        with app.requestcontext():
            app.view()
            assert v1.call_count == 1
            assert v2.call_count == 0

        with app.requestcontext_post():
            app.view()
            assert v1.call_count == 1
            assert v2.call_count == 1


class TestRouteViewFilters(object):

    def exclaim(self, response):
        return response.replace(
            content=[b''.join(response.content_iterator) + b'!'])

    def ask(self, response):
        return response.replace(
            content=[b''.join(response.content_iterator) + b'?'])

    def test_filter_is_applied(self):
        views = fixtures.CBV('test')
        app = FrescoApp()
        app.route('/', GET, views.index_html).filter(self.ask)
        with app.requestcontext('/'):
            assert app.view().content_iterator == [b'test?']

    def test_filter_is_applied_as_route_kwargs(self):
        views = fixtures.CBV('test')
        app = FrescoApp()
        app.route('/', GET, views.index_html, filters=[self.ask])
        with app.requestcontext('/'):
            assert app.view().content_iterator == [b'test?']

    def test_it_applies_multiple_filters_in_order(self):
        app = FrescoApp()
        views = fixtures.CBV('test')
        app.route('/', GET, views.index_html).filter(self.ask, self.exclaim)
        with app.requestcontext('/'):
            assert app.view().content_iterator == [b'test?!']

    def test_it_applies_chained_filter_calls_in_order(self):
        app = FrescoApp()
        views = fixtures.CBV('test')
        app.route('/', GET, views.index_html)\
                .filter(self.ask).filter(self.exclaim)
        with app.requestcontext('/'):
            assert app.view().content_iterator == [b'test?!']


class TestRouteDecorators(object):

    def exclaim(self, func):
        @wraps(func)
        def exclaim(*args, **kwargs):
            response = func(*args, **kwargs)
            return response.replace(
                content=[b''.join(response.content_iterator) + b'!'])
        return exclaim

    def test_decorator_is_applied(self):

        views = fixtures.CBV('test')

        app = FrescoApp()
        app.route('/decorated', GET, views.index_html,
                  decorators=[self.exclaim])
        app.route('/plain', GET, views.index_html)

        with app.requestcontext('/decorated'):
            assert app.view().content_iterator == [b'test!']

        with app.requestcontext('/plain'):
            assert app.view().content_iterator == [b'test']

    def test_decorator_is_applied_with_wrap_method(self):

        views = fixtures.CBV('test')

        app = FrescoApp()
        app.route('/decorated', GET, views.index_html).wrap(self.exclaim)
        app.route('/plain', GET, views.index_html)

        with app.requestcontext('/decorated'):
            assert app.view().content_iterator == [b'test!']

        with app.requestcontext('/plain'):
            assert app.view().content_iterator == [b'test']

    def test_decorator_works_with_urlfor(self):

        views = fixtures.CBV('test')
        app = FrescoApp()
        app.route('/decorated', GET, views.index_html,
                  decorators=[self.exclaim])
        with app.requestcontext():
            assert urlfor(views.index_html, _app=app) == \
                'http://localhost/decorated'

    def test_using_wraps_with_viewspec_doesnt_raise_AttributeError(self):

        def decorator(func):
            @wraps(func)
            def decorator(*args, **kwargs):
                return func(*args, **kwargs)
            return decorator

        class Views(object):
            __routes__ = Route('/',
                               GET, 'index_html', decorators=[decorator]),

            def index_html(self):
                return Response(['hello'])

        app = FrescoApp()
        app.include('/', Views())


class TestPredicates(object):

    def test_predicate_match(self):

        def v1():
            return Response([b'x'])

        def v2():
            return Response([b'y'])

        app = FrescoApp()
        app.route('/', GET, v1, predicate=lambda request: 'x' in request.query)
        app.route('/', GET, v2, predicate=lambda request: 'y' in request.query)

        with app.requestcontext('/?x=1'):
            assert b''.join(app.view().content) == b'x'
        with app.requestcontext('/?y=1'):
            assert b''.join(app.view().content) == b'y'
        with app.requestcontext('/'):
            assert app.view().status_code == 404


class TestRouteNames(object):

    def test_name_present_in_route_keys(self):
        r = Route('/', GET, None, name='foo')
        assert 'foo' in list(r.route_keys())

    def test_name_with_other_kwargs(self):
        r = Route('/', GET, None, name='foo', x='bar')
        assert 'foo' in list(r.route_keys())

    def test_name_cannot_contain_colon(self):
        with pytest.raises(ValueError):
            Route('/', GET, None, name='foo:bar')


class TestRouteCollection(object):

    def test_it_adds_routes_from_constructor(self):
        r1 = Route('/1', GET, None, name='1')
        r2 = Route('/2', POST, None, name='2')
        rc = RouteCollection([r1, r2])
        assert [r.name for r in rc] == ['1', '2']

    def test_it_adds_routecollections_from_constructor(self):
        r1 = Route('/', GET, None, name='1')
        r2 = Route('/', POST, None, name='2')
        r3 = Route('/', POST, None, name='3')
        rc = RouteCollection([r1, RouteCollection([r2, r3])])
        assert [r.name for r in rc] == ['1', '2', '3']

    def test_it_adds_dunderroutes_from_constructor(self):
        r1 = Route('/', GET, None, name='1')
        r2 = Route('/', POST, None, name='2')
        r3 = Route('/', POST, None, name='3')

        class A:
            __routes__ = [r2, r3]

        rc = RouteCollection([r1, A()])
        assert [r.name for r in rc] == ['1', '2', '3']

    def test_get_routes_matches_on_method(self):

        r_get = Route('/', GET, None)
        r_post = Route('/', POST, None)

        rc = RouteCollection([r_post, r_get])

        assert [r.route for r in rc.get_routes('/', GET)] == [r_get]
        assert [r.route for r in rc.get_routes('/', POST)] == [r_post]

    def test_get_routes_matches_on_path(self):

        r1 = Route('/1', GET, None)
        r2 = Route('/2', GET, None)

        rc = RouteCollection([r1, r2])

        assert [r.route for r in rc.get_routes('/1', GET)] == [r1]
        assert [r.route for r in rc.get_routes('/2', GET)] == [r2]

    def test_get_routes_can_match_all_methods(self):

        r1 = Route('/1', GET, None)
        r2 = Route('/1', POST, None)

        rc = RouteCollection([r1, r2])
        assert [r.route for r in rc.get_routes('/1', None)] == [r1, r2]

    def test_route_returns_traversal_information_on_nested_routes(self):

        a = RouteCollection()
        b = RouteCollection()

        a.route('/harvey', GET, lambda: None)
        b.route('/harvey', GET, lambda: None)

        a.delegate('/rabbit', b)
        b.delegate('/hole', a)

        r = next(a.get_routes('/rabbit/hole/rabbit/harvey', None))
        assert r.collections_traversed == [(a, ''),
                                           (b, '/rabbit'),
                                           (a, '/rabbit/hole'),
                                           (b, '/rabbit/hole/rabbit')]

    def test_pathfor_works_with_positional_args(self):
        view = Mock(return_value=Response())
        rc = RouteCollection([Route('/<:str>', GET, view)])
        assert rc.pathfor(view, 'x') == '/x'

    def test_replace_raises_route_not_found(self):
        a = RouteCollection()
        view = Mock(return_value=Response())
        a.route('/harvey', GET, view, name='harvey')
        with pytest.raises(RouteNotFound):
            a.replace('rabbit', None)

    def test_replace_selects_routes_by_name(self):
        a = RouteCollection()
        oldroute = Route('/', GET, Mock(), name='harvey')
        newroute = Route('/', GET, Mock())
        a.add_route(oldroute)
        a.replace('harvey', newroute)
        assert a.__routes__ == [newroute]

    def test_replace_selects_routes_by_view(self):
        a = RouteCollection()
        view = Mock(return_value=Response())
        oldroute = Route('/', GET, view)
        newroute = Route('/', GET, Mock())
        a.add_route(oldroute)
        a.replace(view, newroute)
        assert a.__routes__ == [newroute]

    def test_can_add_a_list_to_a_routecollection(self):
        r1 = Route('/', GET, Mock())
        r2 = Route('/', GET, Mock())
        assert (RouteCollection([r1]) + [r2]).__routes__ == [r1, r2]

    def test_can_add_route_to_routecollection(self):
        r1 = Route('/', GET, Mock())
        r2 = Route('/', GET, Mock())
        assert (RouteCollection([r1]) + r2).__routes__ == [r1, r2]

    def test_can_add_routecollection_to_route(self):
        r1 = Route('/', GET, Mock())
        r2 = Route('/', GET, Mock())
        assert (r1 + RouteCollection([r2])).__routes__ == [r1, r2]

    def test_can_add_routecollections(self):
        r1 = Route('/', GET, Mock())
        r2 = Route('/', GET, Mock())
        assert (RouteCollection([r1]) + RouteCollection([r2])).__routes__ == \
                [r1, r2]

    def test_routecollections_can_be_used_in_classes(self):
        class MyViews(object):
            __routes__ = RouteCollection([
                Route('/', GET, 'view')])

            def view(self):
                return Response()

        v = MyViews()
        app = FrescoApp()
        app.include('/', v)
        assert [r.route.getview(GET)
                for r in app.get_routes('/', GET)] == [v.view]

    def test_routecollections_in_classes_can_be_manipulated(self):
        class MyViews(object):
            __routes__ = RouteCollection([
                Route('/', GET, 'view')])

            def view(self):
                return Response()

        class MyOtherViews(MyViews):
            __routes__ = copy(MyViews.__routes__)
            __routes__.replace('view', Route('/', GET, 'another_view'))

            def another_view(self):
                return Response()

        v = MyOtherViews()
        app = FrescoApp()
        app.include('/', v)
        assert [r.route.getview(GET)
                for r in app.get_routes('/', GET)] == [v.another_view]

    def test_add_prefix_returns_prefixed_collection(self):
        rc = RouteCollection([Route('/fish', GET, None),
                              Route('/beans', GET, None)])
        prefixed = rc.add_prefix('/jelly')
        assert [str(r.pattern) for r in prefixed] == \
                ['/jelly/fish', '/jelly/beans']

    def test_it_binds_routes_to_an_instance(self):
        views = fixtures.CBV('test')
        rc = RouteCollection([views])
        view = next(rc.get_routes('/', GET)).route.getview(GET)
        assert_method_bound_to(view, views)

    def test_it_binds_routes_to_an_instance_via_include(self):
        views = fixtures.CBV('test')
        rc = RouteCollection([])
        rc.include('/', views)
        view = next(rc.get_routes('/', GET)).route.getview(GET)
        assert_method_bound_to(view, views)

    def test_including_twice_does_not_rebind_instance(self):
        views = fixtures.CBV('test')
        rc = RouteCollection([])
        rc.include('/', views)
        rc2 = RouteCollection([])
        rc2.include('/', rc)
        view = next(rc2.get_routes('/', GET)).route.getview(GET)
        assert_method_bound_to(view, views)


class TestRoutefor(object):

    def test_routefor_with_view_function(self):

        def view():
            return Response(['ok'])

        app = FrescoApp()
        route = app.route('/foo', GET, view)

        with app.requestcontext():
            assert routefor(view) == route

    def test_routefor_with_string(self):
        app = FrescoApp()
        route = app.route('/myviewfunc', GET, fixtures.module_level_function)
        with app.requestcontext():
            assert routefor('fresco.tests.fixtures.module_level_function') == \
                route

    def test_routefor_generates_first_route(self):

        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        r1 = app.route('/1', GET, myviewfunc)
        app.route('/2', GET, myviewfunc)
        with app.requestcontext():
            assert routefor(myviewfunc) == r1


class TestDelegatedRoutes(object):

    def test_dispatch_to_delegated_route(self):

        def hello():
            return Response([b'hello'])

        inner = FrescoApp()
        inner.route('/hello', GET, hello)

        outer = FrescoApp()
        outer.delegate('/say', inner)

        with outer.requestcontext('/say/hello'):
            assert b''.join(outer.view().content) == b'hello'

    def test_url_variables_are_passed(self):

        hello = Mock(return_value=Response())

        inner = FrescoApp()
        inner.route('/<i:str>', GET, hello)

        outer = FrescoApp()
        outer.delegate('/<o:str>', inner)

        with outer.requestcontext('/foo/bar'):
            outer.view()
            hello.assert_called_with(i='bar', o='foo')

    def test_delegation_to_dynamic_routes(self):

        result = []

        class MyRoutes(object):
            __routes__ = [Route('/<inner:int>/view', GET, 'view')]

            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def view(self, **kwargs):
                result.append((self, kwargs))
                return Response()

        app = FrescoApp()
        app.delegate('/<outer:str>', MyRoutes, dynamic=True)
        with app.requestcontext('/two/2/view'):
            app.view()
            instance, inner_kwargs = result[0]
            assert inner_kwargs == {'inner': 2}
            assert instance.kwargs == {'outer': 'two'}

    def test_dynamic_routes_are_never_shared(self):

        result = []

        class MyRoutes(object):
            __routes__ = [Route('', GET, 'view')]

            def __init__(self, value):
                self.value = value

            def view(self):
                result.append(self.value)
                return Response()

        app = FrescoApp()
        app.delegate('/<value:str>', MyRoutes, dynamic=True)
        with app.requestcontext('/one'):
            app.view()
            v1 = result.pop()
        with app.requestcontext('/two'):
            app.view()
            v2 = result.pop()
        assert v1 == 'one'
        assert v2 == 'two', v2

    def test_pathfor_with_delegated_route(self):
        inner = FrescoApp()
        inner.route('/<i:str>', GET, lambda: None, name='inner-route')

        outer = FrescoApp()
        outer.delegate('/<o:str>', inner, name='delegation')

        with outer.requestcontext('/foo/bar'):
            assert outer.pathfor('delegation:inner-route',
                                 o='x', i='y') == '/x/y'

    def test_pathfor_with_dynamic_delegated_route(self):

        view = Mock(return_value=Response())

        def routecollectionfactory(*args, **kwargs):
            return RouteCollection([Route('/<i:str>', GET, view,
                                          name='inner-route')])

        rc = RouteCollection()
        rc.delegate('/<o:str>', routecollectionfactory,
                    name='delegation', dynamic=True)

        assert rc.pathfor('delegation:inner-route', o='x', i='y') == '/x/y'

    def test_pathfor_with_dynamic_delegated_route_uses_default_args(self):

        view = Mock(return_value=Response())

        def routecollectionfactory(factoryarg1, factoryarg2):
            return RouteCollection([Route('/<i:str>', GET, view,
                                          name='inner-route')])

        rc = RouteCollection()
        rc.delegate('/<factoryarg1:str>/<factoryarg2:str>',
                    routecollectionfactory,
                    factoryarg1_default='foo',
                    factoryarg2_default=lambda r: 'bar',
                    name='delegation', dynamic=True)

        assert rc.pathfor('delegation:inner-route', i='y') == '/foo/bar/y'

    def test_urlfor_with_dynamic_delegated_route_and_view_self(self):

        result = []

        class MyRoutes(object):
            __routes__ = [Route('/<inner:int>/view', GET, 'view')]

            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def view(self, **kwargs):
                result.append(urlfor(self.view, inner=3))
                return Response()

        app = FrescoApp()
        app.delegate('/<outer:str>', MyRoutes, dynamic=True)
        with app.requestcontext('/two/2/view'):
            app.view()
            assert result == ['http://localhost/two/3/view']

    def test_urlgeneration_with_dynamic_routes(self):

        class Routable(object):
            __routes__ = [Route('/<b:int>', GET, 'view', name='y')]

            def __init__(self, a):
                pass

            def view(self, b):
                return Response()

        app = FrescoApp()
        app.delegate('/<a:str>', Routable, dynamic=True, name='x')
        with app.requestcontext('/two/2/view'):
            assert urlfor('x:y', a='a', b=1) == 'http://localhost/a/1'

    def test_delegated_routes_can_be_included(self):

        view = Mock(return_value=Response())

        inner = RouteCollection([Route('/baz', GET, view)])
        middle = RouteCollection([DelegateRoute('/bar', inner)])
        outer = FrescoApp()
        outer.include('/foo', middle)
        with outer.requestcontext('/foo/bar/baz'):
            outer.view()
            view.assert_called()

    def test_not_found_is_returned(self):

        def inner():
            raise NotFound()

        outer = FrescoApp()
        outer.delegate('/foo', inner, dynamic=True)
        with outer.requestcontext('/foo/bar/baz'):
            response = outer.view()
            assert response.status_code == 404

    def test_not_found_causes_next_route_to_be_tried(self):

        def inner():
            raise NotFound()
        view = Mock(return_value=Response())

        outer = FrescoApp()
        outer.delegate('/foo', inner, dynamic=True)
        outer.route('/foo', GET, view)
        with outer.requestcontext('/foo'):
            outer.view()
            view.assert_called()


class TestConverters(object):

    def test_str_converter_returns_unicode(self):
        from fresco.routing import StrConverter
        s = ustr('abc')
        assert isinstance(StrConverter().from_string(s), ustr)

    def test_register_coverter_acts_as_decorator(self):
        from fresco.routing import Converter, register_converter

        @register_converter('testconverter')
        class MyConverter(Converter):
            def from_string(self, s):
                return 'bar'

        view = Mock(return_value=Response())

        app = FrescoApp()
        app.route('/<:testconverter>', GET, view)
        with app.requestcontext('/foo'):
            app.view()
            assert view.call_args == (('bar',), {}), view.call_args


class TestViewArgs(object):

    def test_it_uses_args(self):
        routes = RouteCollection([Route('/', GET, None, args=(1, 2))])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, args=(1, 2))]

    def test_it_uses_view_args(self):
        routes = RouteCollection([Route('/', GET, None, view_args=(1, 2))])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, args=(1, 2))]

    def test_it_appends_args_extracted_from_path(self):
        routes = RouteCollection([Route('/<:int>', GET, None,
                                        view_args=(1, 2))])
        assert list(routes.get_routes('/3', GET)) == \
                [tms.InstanceOf(RouteTraversal, args=(1, 2, 3))]


class TestViewKwargs(object):

    def test_it_reads_from_route_kwargs(self):
        routes = RouteCollection([Route('/', GET, None, x=1)])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, kwargs={'x': 1})]

    def test_it_reads_from_kwargs(self):
        routes = RouteCollection([Route('/', GET, None, kwargs={'x': 1})])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, kwargs={'x': 1})]

    def test_it_reads_from_view_kwargs(self):
        routes = RouteCollection([Route('/', GET, None, view_kwargs={'x': 1})])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, kwargs={'x': 1})]


class TestRouteClassIsPluggable(object):

    class CustomRoute(Route):
        pass

    def test_it_defaults_to_Route(self):
        routes = RouteCollection()
        assert routes.route_class is Route

    def test_it_accepts_route_class_arg(self):
        routes = RouteCollection(route_class=self.CustomRoute)
        assert routes.route_class is self.CustomRoute

    def test_it_uses_route_class_in_route_method(self):

        def myview():
            pass

        routes = RouteCollection(route_class=self.CustomRoute)
        routes.route('/', GET, myview)

        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal,
                                route=tms.InstanceOf(self.CustomRoute))]

    def test_it_uses_route_class_in_decorator(self):

        routes = RouteCollection(route_class=self.CustomRoute)

        @routes.route('/', GET)
        def myview():
            pass

        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal,
                                route=tms.InstanceOf(self.CustomRoute))]

    def test_custom_route_class_survives_include(self):
        routes = RouteCollection(route_class=self.CustomRoute)

        @routes.route('/', GET)
        def myview():
            pass

        routes2 = RouteCollection()
        routes2.include('/incl', routes)

        assert list(routes2.get_routes('/incl/', GET)) == \
                [tms.InstanceOf(RouteTraversal,
                                route=tms.InstanceOf(self.CustomRoute))]
