Fresco, a web micro-framework for Python
========================================


- Simple, powerful URL routing, request and response objects.
- Lightweight and open to integration: you pick the templating and database libraries you want.
- WSGI compliant: easy integration with your choice of web server, apps and middleware.

A minimal fresco web application:

.. code-block:: python

    from fresco import FrescoApp, GET, Response

    def helloworld():
        return Response(["<h1>Hello World!</h1>"])

    app = FrescoApp()
    app.route('/', GET, helloworld)


Read the `fresco documentation <http://www.ollycope.com/software/fresco/>`_ or
visit the `bitbucket repo <https://bitbucket.com/ollyc/fresco>`_ for more info.
