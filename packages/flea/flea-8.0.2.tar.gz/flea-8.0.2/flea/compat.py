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
import sys
try:
    from http.cookies import BaseCookie
    from urllib.parse import quote, unquote, urlparse, urlunparse, urlencode
except ImportError:
    from Cookie import BaseCookie  # NOQA
    from urlparse import urlparse, urlunparse  # NOQA
    from urllib import quote, unquote, urlencode  # NOQA


if sys.version_info < (3, 0):
    PY2 = True
    string_types = (unicode, str)
    ustr = unicode
else:
    PY2 = False
    string_types = str
    ustr = str
