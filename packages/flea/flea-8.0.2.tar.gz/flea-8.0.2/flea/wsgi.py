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

from __future__ import print_function, absolute_import

from fresco import Request
from fresco.util.http import parse_header
from fresco.util.wsgi import unicode_to_environ
from lxml.html import tostring

from .compat import quote
from .util import is_html, base_url


class PassStateWSGIApp(object):
    """
    A WSGI application that replays the TestAgent's cookies and currently
    loaded response to the downstream UA on the first request,
    thereafter proxies requests to the agent's associated wsgi
    application.

    Used by ``TestAgent.serve``.
    """

    def __init__(self, testagent, initial_path):
        self.first_request_served = False
        self.testagent = testagent
        self.initial_path = initial_path

    def __call__(self, environ, start_response):
        if self.first_request_served:
            return self.testagent.validated_app(environ, start_response)
        if Request(environ).path != self.initial_path:
            return self.redirect_to_initial_path(environ, start_response)
        return self.first_request(environ, start_response)

    def redirect_to_initial_path(self, environ, start_response):
        path = unicode_to_environ(self.initial_path)
        path = quote(path)
        start_response('302 Found', [('Content-Type', 'text/html'),
                                     ('Location', path)])
        return ['<a href="{0}">{0}</a>'.format(path).encode('utf8')]

    def first_request(self, environ, start_response):
        self.first_request_served = True
        response = self.testagent.response
        mimetype, charset = parse_header(response.get_header('Content-Type'))
        charset = dict(charset).get('charset', 'UTF-8')
        self.testagent._read_response()

        if is_html(response) and self.testagent._lxml is not None:
            content = tostring(self.testagent.lxml, encoding=charset)
        else:
            content = self.testagent._body
        assert isinstance(content, bytes)

        if is_html(response):
            original_url = base_url(self.testagent.request.environ)
            served_url = base_url(environ)
            if original_url != served_url:
                content = content.replace(original_url.encode(charset),
                                          served_url.encode(charset))

        response = response.replace(content=[content])
        for key, morsel in self.testagent.cookies.items():
            response = response.add_header('Set-Cookie', morsel.OutputString())
        return response(environ, start_response)
