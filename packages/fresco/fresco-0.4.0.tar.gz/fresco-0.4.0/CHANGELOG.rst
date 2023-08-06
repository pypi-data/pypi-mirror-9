Changelog
=========

0.4.0
------

- Request.cookies now maps names to values (not cookie objects), simplifying
  cookie handling and bringing us in line with how most other frameworks treat
  cookies.
  **This change breaks backwards compatibility**.
- The ``maxage`` and ``http_only`` arguments to
  ``Cookie.__init__`` and ``Response.add_cookie``
  have been renamed to ``max_age`` and ``httponly`` respectively,
  reflecting the spelling used in the Set-Cookie header
  ('Max-Age' and 'HttpOnly').
  **This change breaks backwards compatibility**.
- Changed ``FrescoApp``'s constructor to have the same signature as
  ``RouteCollection``. You can get the old behavior by using the ``views`` and
  ``path`` keyword arguments.
  **This change breaks backwards compatibility**.
- Removed blinker dependency and associated signals. These were never
  documented and the application hooks added in this version provide a more
  flexible replacement.
  **This change breaks backwards compatibility**.
- Removed the deprecated ``url`` method added to view functions
  **This change breaks backwards compatibility**.

0.3.14
------

- Added ``request.is_secure`` property.
- Added ``filters`` keyword argument to ``Route``.
- Calling ``Response()`` with no arguments now creates a ``204 No Content``
  response.
- Calling ``Response('some string')`` no longer causes the string to be output
  byte-by-byte.
- Added ``Response.add_vary`` method.
- Response cookies have had the ``Version`` attribute removed, bringing them
  in line with RFC6265.
- Added hooks to ``FrescoApp``: ``process_request``, ``process_response``,
  ``process_view``, ``process_exception``, ``process_http_error_response``,
  and ``finish_request``.
- Deprecated blinker signals in ``FrescoApp``.
  ``FrescoApp.route_matched``, ``FrescoApp.view_finished``
  and ``FrescoApp.before_response`` should be
  replaced by the equivalent appliation hooks (``process_request``,
  ``process_view`` and ``process_response`` respectively).

0.3.13
------

- Bugfix for ``FrescoApp.requestcontext_put`` and
  ``FrescoApp.requestcontext_patch`` which were raising a TypeError

0.3.12
------

- Added ``FrescoApp.requestcontext_post``,
  ``FrescoApp.requestcontext_put``,
  ``FrescoApp.requestcontext_patch`` and
  ``FrescoApp.requestcontext_delete``,
  to simplify direct testing of view functions.
- Added a flag to disable middleware processing in requestcontext, eg
  ``FrescoApp.requestcontext(middleware=False)``. For middleware heavy stacks
  this may be used to speed up testing of individual views.

0.3.11
------

- Added ``request.body`` and ``request.body_bytes`` properties
- Added a ``request.get_json`` method to access JSON request payloads
- Deprecated ``view_function.url()``
- Added ``RouteCollection.remove`` and ``RouteCollection.replace`` methods,
  making it easier to extend and modify RouteCollections.

0.3.10
------

- Invalid character data in the request body no longer causes an exception.

0.3.9
-----

- ``fresco.decorators.extract_*`` methods are now deprecated in favour of the
  functions in ``fresco.routeargs``
- Fixed an error in RouteArg when using a conversion function and a value is
  not supplied
- Added ``fresco.decorators.json_response``
- Added support for python 3.4 and dropped support for python 3.2

0.3.8
-----

- A new ``routearg`` function allows RouteArgs to be constructed dynamically
- Renamed ``Route.decorate`` to ``Route.wrap``
- Added ``Route.filter`` to pipe the output of the view through a custom filter
  function


0.3.7
-----

- Bugfix for RouteArg when using a default value
- Bugfix for urlfor when using positional arguments.
- Added decorate method for Route objects.
- Added fresco.routing.register_converter class decorator for simpler
  registration of routing pattern converters.
- Added fresco.util.common.object_or_404.
- Bugfix: fresco.util.urls.make_query no longer sorts key value pairs into
  alphabetical order, but preserves the original ordering.
- fresco.static.serve_static_file now checks for certain malformed requests
  and returns an HTTP bad request status

0.3.6
-----

- Improved startup time for apps with lots of middleware
- fresco.context no longer copies values from the parent when setting up
  a new request context. This makes it easier for libraries using
  fresco.context to cache resources per-request.
- Bugfix for FrescoApp.requestcontext, which was creating duplicate context
  frames.
- FrescoApp.view_finished signal now passes the request object to subscribers
- Route objects can now take a tuple of positional args to pass to views::

      Route(POST, '/contact', args=('anne@example.com',))

- The route class used by RouteCollection is now configurable, allowing apps to
  define custom routing classes.
- fresco.routearg.RouteKwarg has been renamed to ``RouteArg`` and now works for
  positional arguments via ``Route(..., args=...)``
- ``Request.make_url`` now accepts two new optional arguments, ``query_add``
  and ``query_replace``. This facilitates building urls based on the current
  query string with selected values added or replaced.
- Bugfix: improperly encoded paths now cause a 400 bad response to be returned
  rather than raising UnicodeDecodeError

0.3.5
-----

- FrescoApp.requestcontext() now invokes all registered middleware. This can be
  useful for testing views that rely on middleware to set environ keys or
  provide other services

- RouteArg classes have been expanded and are now in a separate module,
  ``fresco.routeargs``

0.3.4
-----

- Bugfix: Request.form was not handling unicode data in GET requests correctly
- fresco.core.request_class has been moved to FrescoApp.request_class
- Route arguments can take default arguments for url generation
- Added tox for testing: fresco is now tested and works with Python 2.6,
  2.7, 3.2 and 3.3

0.3.3
-----

- Bugfix: Request.make_url was double quoting URLs in some circumstances

0.3.2
-----

- Improved handling for ResponseExceptions raised during route traversal

0.3.1
-----

- Bugfix: routing arguments were being incorrectly converted to bytestrings in
  python2
- Bugfix: urlfor works correctly with dynamic routes

0.3.0
-----

**Note that upgrading to this version will require changes to your
application**

- View functions are no longer passed a request object as a positional argument
- The syntax used to reference views by name has changed from
  ``urlfor('mymodule:view')`` to ``urlfor('mymodule.view')``.
- Routing: named routes are now supported, eg ``Route('/', GET, myview,
  name='homepage')``. These can later be accessed by eg ``urlfor('homepage')``.
  The old route tagging facility has been removed.
- Routing: Support for delegating paths to other routeable objects
- fresco.exceptions.NotFoundFinal has been replaced by NotFound(final=True)
- Experimental Python 3 support

0.2.4
-----

- Bugfix: setting the logger property on a FrescoApp no longer causes errors

0.2.3
-----

- FrescoApp objects now have an options dictionary for application level
  settings
- Added serve_static_file function
- Added support for signals with blinker
- urlfor now requires fully qualified module names if called with a string
  argument

0.2.2
-----

- Bug: URL generation broken when HTTP_HOST does not contain port number

0.2.1
-----

- Bugfixes for beaker session support and broken URL generation when
  'X-Forwarded-SSL: off' header supplied

0.2.0
-----

- Removed dependency on Pesto

0.1 (unreleased)
----------------

