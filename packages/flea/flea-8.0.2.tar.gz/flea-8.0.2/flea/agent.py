# coding: UTF-8

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

from __future__ import absolute_import

from io import BytesIO, StringIO
from itertools import chain
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from wsgiref.simple_server import make_server
import copy
import logging
import os
import webbrowser
import wsgiref.validate
import re

from fresco import Request, Response
from fresco.util.http import parse_header
from fresco.util.wsgi import unicode_to_environ
from lxml.html import fromstring, tostring

from .compat import PY2, BaseCookie, unquote, ustr, string_types
from .html import ElementWrapper
from .exceptions import BadStatusError, NotARedirectError
from .wsgi import PassStateWSGIApp
from .util import url_join_same_server, urlencode_wrapper, parse_cookies

__all__ = ['Agent']


class History(list):

    def __init__(self, *args, **kwargs):
        super(History, self).__init__(*args, **kwargs)
        self.checkpoints = {}

    def checkpoint(self, name, value):
        """
        Create a named checkpoint
        """
        self.checkpoints[name] = value

    def __getitem__(self, item):
        if isinstance(item, string_types):
            return self.checkpoints[item]
        return super(History, self).__getitem__(item)

    def __add__(self, item):
        ob = History(super(History, self).__add__(item))
        ob.checkpoints = self.checkpoints.copy()
        if hasattr(item, 'checkpoints'):
            ob.checkpoints.update(item.checkpoints)
        return ob


class Agent(object):
    """
    A ``Agent`` object provides a user agent for the WSGI application under
    test.

    Key methods and properties:

        - ``get(path)``, ``post(path)``, ``post_multipart`` - create get/post
          requests for the WSGI application and return a new ``Agent``
          object

        - ``request``, ``response`` - the
          `Fresco <http://pypi.python.org/pypi/fresco>`_
          request and response objects associated with the last WSGI request.

        - ``body`` - the body response as a bytes object

        - ``body_decoded`` - the body response decoded into a string

        - ``lxml`` - the lxml representation of the response body (only
           applicable for HTML responses)

        - ``reset()`` - reset the Agent object to its initial state,
           discarding any form field values

        - ``find()`` (or dictionary-style attribute access) - evalute the given
           xpath expression against the current response body and return a
           ``ResultWrapper`` object.
    """

    response_class = Response

    default_charset = 'UTF-8'

    _lxml = None
    _body = None

    environ_defaults = {
        'SCRIPT_NAME': "",
        'PATH_INFO': "",
        'QUERY_STRING': "",
        'SERVER_NAME': "localhost",
        'SERVER_PORT': "8080",
        'SERVER_PROTOCOL': "HTTP/1.0",
        'REMOTE_ADDR': '127.0.0.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'flea.testing': True,
    }

    def __init__(self, app, environ=None, response=None, cookies=None,
                 history=None, validate_wsgi=True, host='localhost',
                 port='8080', loglevel=None, logger=None,
                 original_environ=None,
                 environ_defaults=None,
                 close_response=True):
        """
        Initialize the ``Agent`` object.

        :param app: The WSGI app under test
        :param validate_wsgi: If True, the application under test will be
                              wrapped in ``wsgiref.validate.validator``
                              middleware.
        :param host: The host to use for the WSGI environ ``SERVER_NAME`` key
        :param port: The port to use for the WSGI environ ``SERVER_PORT`` key
        :param loglevel: Controls logging verbosity, eg ``logging.DEBUG``
                         ``None`` means no logging
        :param logger: A ``logging.Logger`` object. If supplied ``loglevel``
                       will be ignored.
        :param close_response: If ``True`` the response iterator will be
                               read from and closed immediately. If
                               ``False``, it is up to the caller to handle
                               closing the WSGI iterator at the end of the
                               request.

        The following parameters are intended for internal use only:

        :param environ_defaults: A list of default WSGI environ values
        :param history: The history list
        :param cookie: The cookie store to use for the Agent.
        :param environ: The WSGI request environ used for the current request
        :param original_environ: A snapshot of the WSGI request environ for the
                                 from before the WSGI request was made.
                                 Additional keys inserted by the WSGI app
                                 will not be present.
        :param response: The ``fresco.response.Response`` object associated
                         with the current request
        """
        if logger is not None:
            logger = logger
        elif loglevel is not None:
            logger = logging.getLogger(self.__class__.__name__)
            logger.setLevel(loglevel)
        else:
            logger = None

        self.options = {
            'host': host,
            'port': port,
            'validate_wsgi': validate_wsgi,
            'logger': logger,
            'close_response': close_response,
        }

        self.environ = environ
        self.response = response
        if environ:
            if not original_environ:
                original_environ = environ
            self.request = Request(original_environ.copy())
            self.original_environ = original_environ
        else:
            self.request = None
            self.original_environ = {}

        #: The original wsgi application
        self.app = app

        if self.options['validate_wsgi']:
            self.validated_app = wsgiref.validate.validator(app)
        else:
            self.validated_app = app

        if cookies:
            self.cookies = cookies
        else:
            self.cookies = BaseCookie()

        if history:
            self.history = history
        else:
            self.history = History()

        if response:
            _, opts = parse_header(response.get_header('Content-Type'))
            self.charset = opts.get('charset', self.default_charset)
            self.cookies.update(parse_cookies(response))
            if self.options['close_response']:
                self._read_response()
        else:
            self.charset = self.default_charset

        # Stores file upload field values in forms
        self.file_uploads = {}

        self.environ_defaults = (environ_defaults or self.environ_defaults)\
                                    .copy()
        self.environ_defaults.update({'SERVER_NAME': host,
                                      'SERVER_PORT': str(port)})

    def make_environ(self, REQUEST_METHOD='GET', PATH_INFO='', wsgi_input=b'',
                     **kwargs):
        """
        Return a dictionary suitable for use as the WSGI environ.

        PATH_INFO must be URL encoded. As a convenience it may also contain a
        query string portion which will be used as the QUERY_STRING WSGI
        variable.
        """
        SCRIPT_NAME = kwargs.pop('SCRIPT_NAME',
                                 self.environ_defaults["SCRIPT_NAME"])

        if SCRIPT_NAME and SCRIPT_NAME[-1] == '/':
            SCRIPT_NAME = SCRIPT_NAME[:-1]
            PATH_INFO = '/' + PATH_INFO

        if '?' in PATH_INFO:
            if 'QUERY_STRING' in kwargs:
                raise AssertionError("QUERY_STRING specified both in "
                                     "PATH_INFO and as argument to "
                                     "make_environ")
            PATH_INFO, querystring = PATH_INFO.split('?', 1)
            kwargs['QUERY_STRING'] = unicode_to_environ(querystring)

        assert re.match(r'^[/A-Za-z0-9\-._~!$/&\'()*+,;=:@%]*$', PATH_INFO), \
            "Path info not URL encoded"

        assert not re.search(r'%(?![A-F0-9]{2})', PATH_INFO), \
            "Path info not URL encoded"

        # Unquote requires a string argument
        if isinstance(PATH_INFO, bytes):
            PATH_INFO = PATH_INFO.decode('ascii')
        if isinstance(SCRIPT_NAME, bytes):
            SCRIPT_NAME = SCRIPT_NAME.decode('ascii')

        # 'caf%C3%A9' -> 'caf\xc3\xa9'
        PATH_INFO = unquote(PATH_INFO)
        SCRIPT_NAME = unquote(SCRIPT_NAME)

        # Python 3 unquotes to unicode correctly but Python 2 gets it wrong
        if PY2:
            # 'caf\xc3\xa0' -> b'caf\xc3\xa9' -> 'café'
            PATH_INFO = PATH_INFO.encode('latin1').decode(self.charset)
            SCRIPT_NAME = SCRIPT_NAME.encode('latin1').decode(self.charset)

        PATH_INFO = unicode_to_environ(PATH_INFO)
        SCRIPT_NAME = unicode_to_environ(SCRIPT_NAME)

        environ = self.environ_defaults.copy()
        environ.update(kwargs)
        for key, value in kwargs.items():
            if '.' not in key and isinstance(value, ustr):
                value = unicode_to_environ(value)
            environ[key.replace('wsgi_', 'wsgi.')] = value

        if isinstance(wsgi_input, bytes):
            wsgi_input = BytesIO(wsgi_input)

        environ.update({
            'REQUEST_METHOD': REQUEST_METHOD,
            'SCRIPT_NAME': SCRIPT_NAME,
            'PATH_INFO': PATH_INFO,
            'wsgi.input': wsgi_input,
            'wsgi.errors': StringIO(),
        })

        if environ['SCRIPT_NAME'] == '/':
            environ['SCRIPT_NAME'] = ''
            environ['PATH_INFO'] = '/' + environ['PATH_INFO']

        while PATH_INFO.startswith('//'):
            PATH_INFO = PATH_INFO[1:]

        return environ

    def _wsgi_request(self, environ, follow=True, history=False,
                      check_status=True):
        """
        Low level entry point for making requests to the WSGI application.

        Return a Agent object representing the new state resulting from the
        request.

        :param environ: WSGI environ to be used for the request

        :param follow: If false, redirect responses will not be followed

        :param history: If true, a new entry will be added to the history
                        attribute for the resulting Agent object

        :param check_status: If true, any non success HTTP status code will
                             result in an AssertionError being raised
        """
        path = environ['SCRIPT_NAME'] + environ['PATH_INFO']
        environ['HTTP_COOKIE'] = '; '.join(
            '%s=%s' % (key, morsel.value)
            for key, morsel in self.cookies.items()
            if path.startswith(morsel['path'])
        )

        if history:
            history = self.history + [self]
        else:
            history = self.history

        if self.options['logger']:
            request = Request(environ.copy())
            self.options['logger'].info("%s %s", request.method, request.url)
            if environ['HTTP_COOKIE']:
                self.options['logger'].debug("Cookie: %s",
                                             environ['HTTP_COOKIE'])
            postdata = environ['wsgi.input'].getvalue()
            environ['wsgi.input'].seek(0)
            if postdata:
                self.options['logger'].info("wsgi.input: %r", postdata)

        original_environ = environ.copy()
        response = self.response_class.from_wsgi(
                self.validated_app, environ, self.start_response)
        agent = self.__class__(
            self.app,
            environ,
            response,
            self.cookies,
            history,
            original_environ=original_environ,
            environ_defaults=self.environ_defaults,
            **self.options
        )
        if self.options['logger']:
            self.options['logger'].info('Response: %s', response.status)
            for name, value in response.headers:
                self.options['logger'].debug('Response: %s: %s', name, value)

        if check_status and response.status[0] not in '23':
            raise BadStatusError("%s %r returned HTTP status %r" % (
                environ['REQUEST_METHOD'],
                path,
                response.status
            ))

        if follow:
            return agent.follow_all()
        return agent

    def _request(self, PATH_INFO='/', data=None, charset='UTF-8', follow=True,
                 history=True, check_status=True,
                 content_type='application/x-www-form-urlencoded',
                 method='POST',
                 **kwargs):
        """
        Make an HTTP request to the application and return the response.

        :param PATH_INFO: The path to request from the application. This must
                          be URL encoded.

        :param data: POST data to be sent to the application. Can be a byte
                     string of the raw post data, a dict or a list of ``(name,
                     value)`` tuples.

        :param charset: Encoding used for any unicode values encountered in
                        ``data``

        :param content_type: The content type header for the posted data. The
                             default is good for testing form submissions, if
                             you want to test an API you may need to change
                             this to something else, eg 'application/json'

        :param follow: If false, redirect responses will not be followed

        :param history: If true, a new entry will be added to the history
                        attribute for the resulting Agent object

        :param check_status: If true, any non success HTTP status code will
                             result in an AssertionError being raised
        """

        if self.request:
            PATH_INFO = url_join_same_server(self.request.url,
                                             PATH_INFO)
        else:
            baseurl = '{0}://{1}:{2}'.format(
                            self.environ_defaults['wsgi.url_scheme'],
                            self.options['host'],
                            self.options['port'])
            PATH_INFO = url_join_same_server(baseurl, PATH_INFO)

        if data is None:
            envargs = kwargs
        else:
            if not isinstance(data, bytes):
                data = urlencode_wrapper(data, encoding=charset)
                data = data.encode('ASCII')
            envargs = {'CONTENT_TYPE': content_type,
                       'CONTENT_LENGTH': unicode_to_environ(ustr(len(data)))}
            envargs.update(kwargs)

        wsgi_input = BytesIO(data)
        wsgi_input.seek(0)

        return self._wsgi_request(
            self.make_environ(
                method,
                PATH_INFO,
                wsgi_input=wsgi_input,
                **envargs
            ),
            follow,
            history,
            check_status,
        )

    def get(self, PATH_INFO='/', data=None, charset='UTF-8', *args, **kwargs):
        kwargs.setdefault('method', 'GET')
        if data is not None:
            kwargs.setdefault(
                'QUERY_STRING', urlencode_wrapper(data, encoding=charset))
            data = None
        return self._request(PATH_INFO, data, charset, *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.get(method='HEAD', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request(method='POST', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request(method='DELETE', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request(method='PUT', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request(method='PATCH', *args, **kwargs)

    def post_multipart(self, PATH_INFO='/', data=None, charset='UTF-8',
                       files=None, *args, **kwargs):
        """
        POST a request to the given URI using multipart/form-data encoding.

        :param PATH_INFO: The path to request from the application. This must
                          be a URL encoded string.

        :param data: POST data to be sent to the application, must be either a
                     dict or list of ``(name, value)`` tuples.

        :param charset: Encoding used for any unicode values encountered in
                        ``data``

        :param files: list of ``(name, filename, content_type, data)`` tuples.
                      ``data`` may be either a byte string, iterator or
                      file-like object.
        """
        if data is None:
            data = {}

        try:
            data = data.items()
        except AttributeError:
            pass

        if files is None:
            files = []

        boundary = b'----------------------------------------BoUnDaRyVaLuE'

        def add_headers(key, value):
            """
            Return a tuple of ``([(header-name, header-value), ...], data)``
            for the given key/value pair
            """
            if isinstance(value, tuple):
                filename, content_type, data = value
                headers = [
                    ('Content-Disposition',
                     'form-data; name="%s"; filename="%s"' %
                            (key, filename)),
                    ('Content-Type', content_type)
                ]
                return headers, data
            else:
                if not isinstance(value, bytes):
                    value = value.encode(charset)
                headers = [('Content-Disposition',
                            'form-data; name="%s"' % (key,))]
                return headers, value

        items = chain(
            (add_headers(k, v) for k, v in data),
            (add_headers(k, (fname, ctype, data))
             for k, fname, ctype, data in files),
        )

        CRLF = b'\r\n'
        post_data = BytesIO()
        post_data.write(b'--' + boundary)
        for headers, data in items:
            post_data.write(CRLF)
            for name, value in headers:
                line = '%s: %s' % (name, value)
                post_data.write(line.encode('ascii'))
                post_data.write(CRLF)
            post_data.write(CRLF)
            if hasattr(data, 'read'):
                copyfileobj(data, post_data)
            elif isinstance(data, bytes):
                post_data.write(data)
            elif isinstance(data, string_types):
                post_data.write(data.encode('ascii'))
            else:
                for chunk in data:
                    post_data.write(chunk)
            post_data.write(CRLF)
            post_data.write(b'--' + boundary)
        post_data.write(b'--' + CRLF)
        length = post_data.tell()
        kwargs.setdefault('method', 'POST')
        kwargs.setdefault('CONTENT_LENGTH', str(length))
        kwargs.setdefault('CONTENT_TYPE', unicode_to_environ(
                                            'multipart/form-data; boundary=' +
                                            boundary.decode('ascii')))

        return self._request(PATH_INFO, post_data.getvalue(),
                             charset=charset, **kwargs)

    def reload(self, follow=True, check_status=True):
        """
        Reload the current page, if necessary re-posting any data.

        Form fields that have been filled in on the loaded page, they will be
        refilled on the reloaded page, provided that the reloaded page has
        exactly the same fields present in the same order.
        """
        if self.options['logger']:
            self.options['logger'].debug("Reload: %s", self.request.path)
        env = self.original_environ.copy()

        wsgi_input = env['wsgi.input']
        if isinstance(wsgi_input, wsgiref.validate.InputWrapper):
            wsgi_input = wsgi_input.input
        wsgi_input.seek(0)
        env['wsgi.input'] = wsgi_input
        agent = self._wsgi_request(env, follow=follow,
                                   check_status=check_status)

        if self._lxml is not None:
            for src, dst in zip(self.find('//input|//textarea|//option'),
                                agent.find('//input|//textarea|//option')):
                if not all([src.tag == dst.tag,
                            src.attrib.get('name') == dst.attrib.get('name'),
                            src.attrib.get('type') == dst.attrib.get('type')]):
                    break

                if src.tag == 'input' and \
                        src.attrib.get('type') in ('radio', 'checkbox'):
                    if 'checked' in src.attrib:
                        dst.attrib['checked'] = src.attrib['checked']
                    elif 'checked' in dst.attrib:
                        del dst.attrib['checked']

                elif src.tag == 'option':
                    if 'selected' in src.attrib:
                        dst.attrib['selected'] = src.attrib['selected']
                    elif 'selected' in dst.attrib:
                        del dst.attrib['selected']

                elif src.tag == 'textarea':
                    dst.el.text = src.el.text

                else:
                    if 'value' in src.attrib:
                        dst.attrib['value'] = src.attrib['value']
                    elif 'value' in dst.attrib:
                        del dst.attrib['value']

        return agent

    def checkpoint(self, name):
        """
        Checkpoint the history at the current location. The current agent state
        can later be retrieved with ``agent.history[name]``.
        """
        self.history.checkpoint(name, self)

    def start_response(self, status, headers, exc_info=None):
        """
        No-op implementation.
        """

    def __str__(self):
        if self.response:
            return str(self.response)
        else:
            return super(Agent, self).__str__()

    def _read_response(self):

        if not self.response:
            return
        if self._body is not None:
            return
        try:
            self._body = b''.join(self.response.content)
        finally:
            try:
                self.response.content.close()
            except AttributeError:
                pass

    @property
    def body_bytes(self):
        """
        The body of the response

        :rtype: bytes
        """
        if self._body is None:
            self._read_response()
        return self._body

    @property
    def body(self):
        if self.body_bytes is None:
            return None
        return self.body_bytes.decode(self.charset)

    @property
    def lxml(self):
        if self._lxml is not None:
            return self._lxml
        self.reset()
        return self._lxml

    @property
    def root_element(self):
        return ElementWrapper(self, self.lxml)

    def html(self):
        """
        Return an HTML representation of the (html) response's root element

        :rtype: unicode string
        """
        return self.root_element.html()

    def pretty(self):
        """
        Return an pretty-printed string representation of the (html) response
        body

        :rtype: unicode string
        """
        return self.root_element.pretty()

    def striptags(self):
        """
        Return the (html) response's root element, with all tags stripped out,
        leaving only the textual content. Normalizes all sequences of
        whitespace to a single space.

        Use this for simple text comparisons when testing for document content

        :rtype: unicode string
        """
        return self.root_element.striptags()

    def __contains__(self, what):
        return what in self.body

    def reset(self):
        """
        Reset the lxml document, abandoning any changes made
        """
        self._lxml = fromstring(self.body)

    def find(self, path, namespaces=None, **kwargs):
        """
        Return elements matching the given xpath expression.

        If the xpath selects a list of elements a ``ResultWrapper`` object is
        returned.

        If the xpath selects any other type (eg a string attribute value), the
        result of the query is returned directly.

        For convenience that the EXSLT regular expression namespace
        (``http://exslt.org/regular-expressions``) is prebound to
        the prefix ``re``.
        """
        return self.root_element.find(path, namespaces, **kwargs)

    def __call__(self, path, flavor='auto', **kwargs):
        return self.root_element(path, flavor, **kwargs)

    def __getitem__(self, path):
        return self.root_element[path]

    def css(self, selector):
        """
        Return elements matching the given CSS Selector (see
        ``lxml.cssselect`` for documentation on the ``CSSSelector`` class.
        """
        return self.root_element.css(selector)

    def click(self, linkspec, flavor='auto', ignorecase=True, index=0,
              follow=True, check_status=True, **kwargs):
        """
        Click the link matched by ``linkspec``. See :meth:`findlinks` for a
        description of the link finding parameters

        :param linkspec:   specification of the link to be clicked
        :param flavor:     if ``css``, ``linkspec`` must be a CSS selector,
                           which must returning one or more links; if
                           ``xpath``, ``linkspec`` must be an XPath expression
                           returning one or more links; any other value will be
                           passed to :meth:`findlinks`.
        :param ignorecase: (see :meth:`findlinks`)
        :param index:      index of the link to click in the case of multiple
                           matching links
        """
        if flavor == 'css':
            links = self.css(linkspec, **kwargs)
        elif flavor == 'xpath':
            links = self.find(linkspec, **kwargs)
        else:
            links = self.findlinks(linkspec, flavor, ignorecase, **kwargs)
        return links[index].click(follow=follow, check_status=check_status)

    def findlinks(self, linkspec, flavor='auto', ignorecase=True, **kwargs):
        """
        Return a :class:`ResultWrapper` of links matched by ``linkspec``.

        :param linkspec:   specification of the link to be clicked
        :param ignorecase: if ``True``, the link search will be case
                           insensitive
        :param flavor:     one of ``auto``, ``text``, ``contains``,
                         ``startswith``, ``re``

        The ``flavor`` parameter is interpreted according to the following
        rules:

        - if ``auto``: detect links based on the following criteria:

            - if ``linkspec`` is a regular expression or otherwise has a
                ``search`` method, this will be used to match links.

            - if ``linkspec`` is callable, each link will be tested
                against it in turn, and the first link that returns True
                will be selected.

            - otherwise ``contains`` matching will be used

        - if ``text``: for links where the text of the link is ``linkspec``
        - if ``contains``: for links where the link text contains ``linkspec``
        - if ``startswith``: for links where the link text contains
          ``linkspec``
        - if ``re``: for links where the text of the link matches ``linkspec``
        """

        links = self.find('//a')

        if flavor == 'auto':
            if callable(linkspec):
                return links.filter(linkspec)
            elif hasattr(linkspec, 'search') and callable(linkspec.search):
                return links.filter_on_text(linkspec.search)
            else:
                flavor = 'contains'

        if ignorecase and flavor in ('text', 'contains', 'startswith'):
            linkspec = linkspec.lower()
            normcase = lambda x: x.lower()
        else:
            normcase = lambda x: x

        if flavor == 'text':
            matcher = lambda text, l=linkspec: l == normcase(text)

        elif flavor == 'contains':
            matcher = lambda text, l=linkspec: l in normcase(text)

        elif flavor == 'startswith':
            matcher = lambda text, l=linkspec: normcase(text).startswith(l)

        elif flavor == 're':
            flags = re.I if ignorecase else 0
            matcher = re.compile(linkspec, flags).search

        else:
            raise AssertionError("bad flavor: " + flavor)

        return links.filter_on_text(matcher)

    def _click(self, el, follow=True, check_status=True):
        href = el.attrib['href']
        if '#' in href:
            href = href.split('#')[0]
        return self.get(href, follow=follow, check_status=check_status)

    def follow(self):
        """
        If response has a ``30x`` status code, fetch (``GET``) the redirect
        target. No entry is recorded in the agent's history list.
        """
        if not (300 <= int(self.response.status.split()[0]) < 400):
            raise NotARedirectError(
                "Can't follow non-redirect response (got %s for %s %s)" % (
                    self.response.status,
                    self.request.method,
                    self.request.path
                )
            )

        return self.get(
            self.response.get_header('Location'),
            history=False,
            follow=False,
        )

    def follow_all(self):
        """
        If response has a ``30x`` status code, fetch (``GET``) the redirect
        target, until a non-redirect code is received. No entries are recorded
        in the agent's history list.
        """

        agent = self
        while True:
            try:
                agent = agent.follow()
            except NotARedirectError:
                return agent

    def new_session(self):
        """
        Return a new Agent with all cookies deleted.
        This gives an easy way to test session expiry.
        """
        agent = copy.copy(self)
        agent.cookies = BaseCookie()
        return agent

    def back(self, count=1):
        return self.history[-abs(count)]

    def showbrowser(self):
        """
        Open the current page in a web browser
        """
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(tostring(self.lxml, encoding='utf8'))
        tmp.close()
        webbrowser.open_new_tab('file:' + tmp.name.replace(os.sep, '/'))

    def serve(self, open_in_browser=True):
        """
        Start a HTTP server for the application under test.

        The host/port used for the HTTP server is determined by the ``host``
        and ``port`` arguments to the ``Agent`` constructor.

        The initial page rendered to the browser will the currently loaded
        document (in its current state - so if changes have been made, eg form
        fields filled these will be present in the HTML served to the browser).
        Any cookies the Agent has stored are also forwarded to the browser.

        Subsequent requests from the browser are then proxied directly to the
        WSGI application under test.
        """
        host = self.environ_defaults['SERVER_NAME']
        port = int(self.environ_defaults['SERVER_PORT'])

        url = self.request.make_url(netloc='{0}:{1}'.format(host, port))
        print("\nStarting HTTP server on {0}\n"
              "Press ctrl-c to exit.".format(url))
        server = make_server(host, port,
                             PassStateWSGIApp(self, self.request.path))
        if open_in_browser:
            webbrowser.open_new_tab(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

    def __enter__(self):
        """
        Provde support for context blocks
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        At end of context block, reset the lxml document
        """
        self.reset()
