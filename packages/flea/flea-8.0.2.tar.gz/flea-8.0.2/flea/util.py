# Copyright 2014 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function, unicode_literals, absolute_import
import re

from fresco.util.urls import url_join
from .compat import (BaseCookie, quote, urlencode, ustr, urlparse,
                     urlunparse)

"""
Various utility functions
"""


def escapeattrib(s):
    return s.replace('&', '&amp;').replace('"', '&quot;')


def base_url(environ):
    """
    Return the base URL for the request (ie everything up to SCRIPT_NAME;
    PATH_INFO and QUERY_STRING are not included)
    """
    url = environ['wsgi.url_scheme'] + '://'

    if environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']

        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        elif environ['SERVER_PORT'] != '80':
                url += ':' + environ['SERVER_PORT']

    url += quote(environ.get('SCRIPT_NAME', ''))
    return url


def _urlencode_items(data, encoding):
    return urlencode([(k if isinstance(k, bytes) else ustr(k).encode(encoding),
                       v if isinstance(v, bytes) else ustr(v).encode(encoding))
                       for k, v in data])


def urlencode_wrapper(data, encoding):
    """
    Wrap stdlib urlencode to :

    - handle fresco style multidict arguments
    - encode unicode strings in the specified charset

    :param data: Data to urlencode as a string, dict or multidict.
    :param encoding: String encoding to use
    :returns: An encoded ``str`` object (a byte string under python 2)
    """
    if hasattr(data, 'allitems'):
        return _urlencode_items(data.allitems(), encoding)
    if hasattr(data, 'items'):
        return _urlencode_items(data.items(), encoding)
    return _urlencode_items(data, encoding)


def is_html(response):
    """
    Return True if the response content-type header indicates an (X)HTML
    content part.
    """
    return re.match(
        r'^(text/html|application/xhtml\+xml)\b',
        response.get_header('Content-Type')
    ) is not None


def parse_cookies(response):
    """
    Return a ``Cookie.BaseCookie`` object populated from cookies parsed from
    the response object
    """
    base_cookie = BaseCookie()
    for item in response.get_headers('Set-Cookie'):
        base_cookie.load(item)
    return base_cookie


def url_join_same_server(baseurl, url):
    """
    Join two urls which are on the same server. The resulting URI will have the
    protocol and netloc portions removed. If the resulting URI has a different
    protocol/netloc then a ``ValueError`` will be raised.

        >>> from flea.util import url_join_same_server
        >>> url_join_same_server('http://localhost/foo', 'bar')
        '/bar'
        >>> url_join_same_server('http://localhost/foo',
        ...                      'http://localhost/bar')
        '/bar'
        >>> url_join_same_server('http://localhost/rhubarb/custard/',
        ...                      '../')
        '/rhubarb/'
        >>> url_join_same_server('http://localhost/foo',
        ...                      'http://example.org/bar')
        Traceback (most recent call last):
          ...
        ValueError: URI links to another server: http://example.org/bar

    """
    url = url_join(baseurl, url)
    url = urlparse(url)
    baseurl = urlparse(baseurl)
    if normalize_host(baseurl.scheme, baseurl.netloc) != \
            normalize_host(url.scheme, url.netloc):
        raise ValueError("URI links to another server: %s (expected %s)" %
                         (urlunparse(url),
                          normalize_host(baseurl.scheme, baseurl.netloc)))
    return urlunparse(('', '') + url[2:])


def normalize_host(scheme, host):
    """
    Normalize the host part of the URL
    """
    host, _, port = host.partition(':')
    if port == '80' and scheme in ('http', None):
        port = ''
    if port == '443' and scheme == 'https':
        port = ''
    if port:
        return '{0}:{1}'.format(host, port)
    return host
