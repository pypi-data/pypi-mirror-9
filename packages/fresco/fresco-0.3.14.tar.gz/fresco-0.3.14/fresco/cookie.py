# Copyright (c) 2007-2012 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.
from __future__ import absolute_import

import copy
try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote, unquote  # NOQA
from datetime import datetime, timedelta
from calendar import timegm
from email.utils import formatdate


class Cookie(object):
    """
    Represents an HTTP cookie.

    See rfc2109, HTTP State Management Mechanism

    Example:

        >>> from fresco.cookie import Cookie
        >>> c = Cookie('session_id', 'abc123')
        >>> c.path = '/cgi-bin'
        >>> c.domain = '.example.org'
        >>> c.path
        '/cgi-bin'
        >>> str(c)
        'session_id=abc123;Domain=.example.org;Path=/cgi-bin'
    """
    attributes = [
        ("Comment", "comment"),
        ("Domain", "domain"),
        ("Expires", "expires"),
        ("Max-Age", "maxage"),
        ("Path", "path"),
        ("Secure", "secure"),
        ("HttpOnly", "http_only"),
    ]

    def __init__(
        self, name, value, maxage=None, expires=None, path=None,
        secure=None, domain=None, comment=None, http_only=False,
        version=1
    ):
        """
        Initialize a ``Cookie`` instance.
        """
        self.name = name
        self.value = value
        self.maxage = maxage
        self.path = path
        self.secure = secure
        self.domain = domain
        self.comment = comment
        self.version = version
        self.expires = expires
        self.http_only = http_only

    def __str__(self):
        """
        Returns a string representation of the cookie in the format, eg
        ``session_id=abc123;Path=/cgi-bin;Domain=.example.com;HttpOnly``
        """
        cookie = ['%s=%s' % (self.name, quote(str(self.value)))]
        for cookie_name, att_name in self.attributes:
            value = getattr(self, att_name, None)
            if att_name == 'http_only':
                if self.http_only:
                    cookie.append(cookie_name)
            elif value is not None:
                cookie.append('%s=%s' % (cookie_name, str(value)))
        return ';'.join(cookie)

    def set_expires(self, dt):
        """
        Set the cookie ``expires`` value to ``datetime`` object ``dt``
        """
        self._expires = dt

    def get_expires(self):
        """
        Return the cookie ``expires`` value as an instance of ``datetime``.
        """
        if self._expires is None and self.maxage is not None:
            if self.maxage == 0:
                # Make sure immediately expiring cookies get a date firmly in
                # the past.
                self._expires = datetime(1980, 1, 1)
            else:
                self._expires = datetime.now() + timedelta(seconds=self.maxage)

        if isinstance(self._expires, datetime):
            return formatdate(timegm(self._expires.utctimetuple()))

        else:
            return self._expires

    expires = property(get_expires, set_expires)


def expire_cookie(cookie_or_name, *args, **kwargs):
    """
    Synopsis:

        >>> from fresco import Response
        >>> from fresco.cookie import expire_cookie
        >>> def view():
        ...     return Response(set_cookie=expire_cookie('X', path='/'))
        ...
        >>> from fresco import FrescoApp
        >>> with FrescoApp().requestcontext() as c:
        ...     print(view().get_header('Set-Cookie'))
        ...
        X=;Expires=Tue, 01 Jan 1980 00:00:00 -0000;Max-Age=0;Path=/
    """
    if isinstance(cookie_or_name, Cookie):
        expire = cookie_or_name
    else:
        expire = Cookie(name=cookie_or_name, value='', *args, **kwargs)
    return Cookie(
        name=expire.name,
        value='',
        expires=datetime(1980, 1, 1),
        maxage=0,
        domain=kwargs.get('domain', expire.domain),
        path=kwargs.get('path', expire.path)
    )


def parse_cookie_header(cookie_string, unquote=unquote):
    """
    Return a list of Cookie objects read from the request headers.

    :param cookie_string: The cookie, eg ``CUSTOMER=FRED; path=/;``

    :param unquote:       A function to decode quoted values. If ``None``
                          values will be left unchanged

    See rfc2109, section 4.4

    The cookie header should be a ';' separated list of name value pairs. If a
    name is prefixed by a '$', then that name is an attribute of the most
    recently (left to right) encountered cookie.  If no cookie has yet been
    parsed then the value applies to the cookie mechanism as a whole.
    """

    if unquote is None:
        unquote = lambda v: v

    if not cookie_string:
        return []
    cookies = []

    # Here we put the $ prefixed attributes that appear *before* a
    # named cookie, to use as a template for other cookies.
    cookie_template = Cookie(None, None)

    for part in cookie_string.split(";"):

        if '=' not in part:
            continue

        k, v = part.strip().split("=", 1)

        # Unquote quoted values ('"..."' => '...')
        if v and '"' == v[0] == v[-1] and len(v) > 1:
            v = v[1:-1]

        if k[0] == '$':
            # Value pertains to most recently read cookie,
            # or cookie_template
            k = k[1:]
            if len(cookies) == 0:
                cookie = copy.copy(cookie_template)
            else:
                cookie = cookies[-1]

            try:
                setattr(cookie, cookie.attribute_dict[k], v)
            except KeyError:
                pass
        else:
            cookies.append(copy.copy(cookie_template))
            cookies[-1].name = unquote(k)
            cookies[-1].value = unquote(v)
    return cookies
