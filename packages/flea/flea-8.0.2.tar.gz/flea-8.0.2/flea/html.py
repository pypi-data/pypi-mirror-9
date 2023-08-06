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
from functools import wraps
import re

from lxml.html import tostring
from lxml.cssselect import CSSSelector, SelectorSyntaxError
from lxml.etree import XPath, XPathError

from .compat import ustr, string_types
from .util import url_join_same_server, escapeattrib

#: Registry for xpath multimethods
xpath_registry = {}

#: EXSLT regular expression namespace URI
REGEXP_NAMESPACE = "http://exslt.org/regular-expressions"


class XPathMultiMethod(object):
    """
    A callable object that has different implementations selected by XPath
    expressions.
    """

    def __init__(self):
        self.__doc__ = ''
        self.__name__ = ''
        self.endpoints = []

    def __call__(self, *args, **kwargs):
        el = args[0]
        el = getattr(el, 'el', el)
        for xpath, func in self.endpoints:
            if el in xpath(el):
                return func(*args, **kwargs)
        raise NotImplementedError("Function %s not implemented for element %r"
                                  % (self.__name__, el,))

    def register(self, xpath, func):
        self.endpoints.append((
            XPath('|'.join('../%s' % item for item in xpath.split('|'))),
            func
        ))
        func_doc = getattr(func, '__doc__', getattr(func, 'func_doc', None))
        if not func_doc:
            return

        # Add wrapped function to the object's docstring
        # Note that ".. comment block" is required to fool rst/sphinx into
        # correctly parsing the indented paragraphs when there is only one
        # registered endpoint.
        doc = 'For elements matching ``%s``:n%s\n\n.. comment block\n\n' % (
                xpath,
                '\n'.join('    %s' % line for line in func_doc.split('\n')))
        self.__doc__ += doc
        self.__name__ = func.__name__


def when(xpath_expr):
    """
    Decorator for methods having different implementations selected by XPath
    expressions.
    """
    def when(func):
        if getattr(func, '__wrapped__', None):
            func = getattr(func, '__wrapped__')
        multimethod = xpath_registry.setdefault(func.__name__,
                                                XPathMultiMethod())
        multimethod.register(xpath_expr, func)
        wrapped = wraps(func)(
            lambda self, *args, **kwargs: multimethod(self, *args, **kwargs)
        )
        wrapped.__wrapped__ = func
        wrapped.func_doc = multimethod.__doc__
        wrapped.__doc__ = multimethod.__doc__
        return wrapped
    return when


class ElementWrapper(object):
    r"""
    Wrapper for an ``lxml.etree`` element, providing additional methods useful
    for driving/testing WSGI applications. ``ElementWrapper`` objects are
    normally created through the ``find``/``css`` methods of ``Agent``
    instance::

        >>> from fresco import Response
        >>> from flea import Agent
        >>> myapp = Response(['<html><body><a href="/">link 1</a>'\
        ...                   '<a href="/">link 2</a></body></html>'])
        >>> agent = Agent(myapp).get('/')
        >>> elementwrapper = agent.find('//a')[0]

    ``ElementWrapper`` objects have many methods and properties implemented as
    ``XPathMultiMethod`` objects, meaning their behaviour varies depending on
    the type of element being wrapped. For example, form elements have a
    ``submit`` method, ``a`` elements have a ``click`` method, and ``input``
    elements have a value property.
    """

    def __init__(self, agent, el):
        self.agent = agent
        self.el = el

    def __str__(self):

        if (len(self.el) == 0 and self.el.text is None):
            return self.html()

        return '<%s%s>...</%s>' % (
            self.el.tag,
            ''.join(' %s="%s"' % (key, escapeattrib(value))
                    for key, value in self.el.attrib.items()),
            self.el.tag,
        )

    __repr__ = __str__

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return (
            self.el is other.el
            and self.agent is other.agent
        )

    def __getattr__(self, attr):
        return getattr(self.el, attr)

    def __call__(self, path, flavor='auto', **kwargs):
        if flavor == 'auto':
            flavor = guess_expression_flavor(path)

        if flavor == 'css':
            return self.css(path, **kwargs)
        else:
            return self.find(path, **kwargs)

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
        ns = {'re': REGEXP_NAMESPACE}
        if namespaces is not None:
            ns.update(namespaces)
        namespaces = ns

        result = self.el.xpath(path, namespaces=namespaces, **kwargs)

        if not isinstance(result, list):
            return result

        return ResultWrapper(
            (ElementWrapper(self.agent, el) for el in result),
            'xpath:' + path
        )

    def css(self, selector):
        """
        Return elements matching the given CSS Selector (see
        ``lxml.cssselect`` for documentation on the ``CSSSelector`` class.
        """
        compiled = CSSSelector(selector)
        return ResultWrapper(
            (ElementWrapper(self.agent, el) for el in compiled(self.el)),
            'css:' + selector
        )

    def __getitem__(self, path):
        result = self.find(path)
        if len(result) == 0:
            raise ValueError("%r matched no elements" % path)
        return result

    @when("a[@href]")  # NOQA
    def click(self, follow=True, check_status=True):
        """
        Follow a link and return a new instance of ``Agent``
        """
        return self.agent._click(self, follow=follow,
                                 check_status=check_status)

    @when("input[@type='submit' or @type='image']|button[@type='submit' or not(@type)]")  # NOQA
    def click(self, follow=True, check_status=True):
        """
        Alias for submit
        """
        return self.submit(follow, check_status=check_status)

    @when("input[@type='file']")  # NOQA
    def _set_value(self, value):
        """
        Set the value of the file upload, which must be a tuple of::

            (filename, content-type, data)

        Where data can either be a byte string or file-like object.
        """
        filename, content_type, data = value
        self.agent.file_uploads[self.el] = (filename, content_type, data)

        # Set the value in the DOM to the filename so that it can be seen when
        # the DOM is displayed
        self.el.attrib['value'] = filename

    @when("input[@type='file']")  # NOQA
    def _get_value(self):
        """
        Return the value of the file upload, which will be a tuple of
        ``(filename, content-type, data)``
        """
        return self.agent.file_uploads.get(self.el)

    @when("input|button")  # NOQA
    def _get_value(self):
        """
        Return the value of the input or button element
        """
        return self.el.attrib.get('value', '')

    @when("input|button")  # NOQA
    def _set_value(self, value):
        """
        Set the value of the input or button element
        """
        self.el.attrib['value'] = value

    value = property(_get_value, _set_value)

    @when("textarea|input|select")  # NOQA
    def input_group(self):
        """
        Return the group of inputs sharing the same name attribute
        """
        return self.form.find(
            """.//*[
                (local-name() = 'input'
                    or local-name() = 'textarea'
                    or local-name() = 'select')
                and (@name='{fieldname}')
            ]
            """.format(fieldname=self.attrib['name'])
        )

    @when("input[@type='checkbox']")  # NOQA
    def submit_value(self):
        """
        Return the value of the selected checkbox element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        if 'checked' in self.el.attrib:
            return self.el.attrib.get('value', 'On')
        return None

    @when("input[@type='radio']")  # NOQA
    def submit_value(self):
        """
        Return the value of the selected radio element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        if 'checked' in self.el.attrib:
            return self.el.attrib.get('value', '')
        return None

    @when("select[@multiple]")  # NOQA
    def submit_value(self):
        """
        Return the value of the selected radio/checkbox element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        return [item.attrib.get('value', item.text)
                for item in self.el.xpath('./option[@selected]')]

    @when("select[not(@multiple)]")  # NOQA
    def submit_value(self):
        """
        Return the value of the selected radio/checkbox element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        try:
            item = self.el.xpath('./option[@selected]')[0]
        except IndexError:
            try:
                item = self.el.xpath('./option[1]')[0]
            except IndexError:
                return None
        return item.attrib.get('value', item.text)

    @when("input[not(@type) or @type != 'submit' and @type != 'image' and @type != 'reset']")  # NOQA
    def submit_value(self):
        """
        Return the value of any other input element as the user
        agent would return it to the server in a form submission.
        """
        if 'disabled' in self.el.attrib:
            return None
        return self.value

    @when("input[@type != 'submit' or @type != 'image' or @type != 'reset']")  # NOQA
    def submit_value(self):
        """
        Return the value of any submit/reset input element
        """
        return None

    @when("textarea")  # NOQA
    def submit_value(self):
        """
        Return the value of any submit/reset input element
        """
        return self.el.text

    submit_value = property(submit_value)

    def _get_checked(self):
        """
        Return True if the element has the checked attribute
        """
        return 'checked' in self.el.attrib

    @when("input[@type='radio']")  # NOQA
    def _set_checked(self, value):
        """
        Set the radio button state to checked (unchecking any others in the
        group)
        """
        for el in self.el.xpath(
            "./ancestor-or-self::form[1]"
            "//input[@type='radio' and @name=$name]",
            name=self.el.attrib.get('name', '')
        ):
            if 'checked' in el.attrib:
                del el.attrib['checked']

        if bool(value):
            self.el.attrib['checked'] = 'checked'
        else:
            if 'checked' in self.el.attrib:
                del self.el.attrib['checked']

    @when("input")  # NOQA
    def _set_checked(self, value):
        """
        Set the (checkbox) input state to checked
        """
        if bool(value):
            self.el.attrib['checked'] = 'checked'
        else:
            try:
                del self.el.attrib['checked']
            except KeyError:
                pass
    checked = property(_get_checked, _set_checked)

    @when("option")  # NOQA
    def _get_selected(self):
        """
        Return True if the given select option is selected
        """
        return 'selected' in self.el.attrib

    @when("option")  # NOQA
    def _set_selected(self, value):
        """
        Set the ``selected`` attribute for the select option element. If the
        select does not have the ``multiple`` attribute, unselect any
        previously selected option.
        """
        if 'multiple' not in \
                self.el.xpath('./ancestor-or-self::select[1]')[0].attrib:
            for el in self.el.xpath("./ancestor-or-self::select[1]//option"):
                if 'selected' in el.attrib:
                    del el.attrib['selected']

        if bool(value):
            self.el.attrib['selected'] = ''
        else:
            if 'selected' in self.el.attrib:
                del self.el.attrib['selected']

    selected = property(_get_selected, _set_selected)

    @property  # NOQA
    @when("input|textarea|button|select|form")
    def form(self):
        """
        Return the form associated with the wrapped element.
        """
        return self.__class__(
            self.agent,
            self.el.xpath("./ancestor-or-self::form[1]")[0]
        )

    @when("input[@type='submit' or @type='image']|button[@type='submit' or not(@type)]")  # NOQA
    def submit(self, follow=True, check_status=True):
        """
        Submit the form, returning a new ``Agent`` object, by clicking on
        the selected submit element (input of
        type submit or image, or button with type submit)
        """
        return self.form.submit(self, follow=follow, check_status=check_status)

    @when("form")  # NOQA
    def submit(self, button=None, follow=True, check_status=True):
        """
        Submit the form, returning a new ``Agent`` object
        """
        method = self.el.attrib.get('method', 'GET').upper()
        data = self.submit_data(button)
        path = url_join_same_server(
            self.agent.request.url,
            self.el.attrib.get('action', self.agent.request.path)
        )
        return {
            ('GET', None): self.agent.get,
            ('POST', None): self.agent.post,
            ('POST', 'application/x-www-form-urlencoded'): self.agent.post,
            ('POST', 'multipart/form-data'): self.agent.post_multipart,
        }[(method, self.el.attrib.get('enctype'))](path, data,
                                                   follow=follow,
                                                   check_status=check_status)

    @when("input[@type='submit' or @type='image']|button[@type='submit' or not(@type)]")  # NOQA
    def submit_data(self):
        """
        Return a list of the data that would be submitted to the server
        in the format ``[(key, value), ...]``, without actually submitting the
        form.
        """
        return self.form.submit_data(self)

    @when("form")  # NOQA
    def submit_data(self, button=None):
        """
        Return a list of the data that would be submitted to the server
        in the format ``[(key, value), ...]``, without actually submitting the
        form.
        """
        data = []
        if isinstance(button, string_types):
            button = self(button)

        if button and 'name' in button.attrib:
            data.append((button.attrib['name'], button.value))
            if button.el.attrib.get('type') == 'image':
                data.append((button.attrib['name'] + '.x', '1'))
                data.append((button.attrib['name'] + '.y', '1'))

        inputs = (ElementWrapper(self.agent, el)
                  for el in self.el.xpath('.//input|.//textarea|.//select'))
        for input in inputs:
            try:
                name = input.attrib['name']
            except KeyError:
                continue
            value = input.submit_value
            if value is None:
                continue

            elif input.attrib.get('type') == 'file' \
                    and isinstance(value, tuple):
                data.append((name, value))

            elif isinstance(value, string_types):
                data.append((name, value))

            else:
                data += [(name, v) for v in value]

        return data

    @when("form")  # NOQA
    def fill(self, *args, **kwargs):
        """
        Fill the current form with data.

        :param \*args: Pairs of ``(selector, value)``
        :param \*\*kwargs: mappings of fieldname to value
        :param _fill_strict: If True, raise an error when a field is not found

        See the documentation for :meth:`_set_value` implementations
        for individual form control types to see how values are processed
        as this varies between text inputs, selects, radio buttons,
        checkboxes etc
        """
        strict = kwargs.pop('_fill_strict', True)

        def check_exists(element, name):
            if len(element) > 0:
                return True

            if strict:
                valid = ', '.join(e.name
                                  for e in self.css('input, textarea, select'))
                raise IndexError(
                    "Couldn't find a form element named {0!r}. "
                    "Valid names are {1}".format(name, valid))

        for selector, value in args:
            element = self(selector)
            if check_exists(element, selector):
                element.fill(value)

        for name, value in kwargs.items():
            path = ".//*[(local-name() = 'input' "\
                   "or local-name() = 'textarea' "\
                   "or local-name() = 'select') "\
                   "and (@name=$name or @id=$name)]"
            element = self.find(path, name=name)
            if check_exists(element, name):
                element.fill(value)

        return self

    @when("form")
    def fill_sloppy(self, *args, **kwargs):
        kwargs['_fill_strict'] = False
        return self.fill(*args, **kwargs)

    @when("input[@type='checkbox']")  # NOQA
    def fill(self, values):

        if values is None:
            values = []

        if isinstance(values, bool):
            self.checked = values

        elif values and all(isinstance(v, bool) for v in values):
            # List of bools, eg ``[True, False, True]``
            for el, checked in zip(self.input_group(), values):
                if checked:
                    el.attrib["checked"] = ""
                elif 'checked' in el.attrib:
                    del el.attrib['checked']

        else:
            # List of values, eg ``['1', '23', '8']``
            found = set()
            values = set(ustr(v) for v in values)
            for el in self.input_group():
                if el.attrib.get('value') in values:
                    el.attrib['checked'] = ""
                    found.add(el.attrib['value'])
                elif 'checked' in el.attrib:
                    del el.attrib['checked']
            if found != values:
                raise AssertionError("Values %r not present"
                                     " in checkbox group %r" %
                                     (values - found,
                                      self.el.attrib.get('name')))

        return self

    @when("input[@type='radio']")  # NOQA
    def fill(self, value):
        """
        Set the value of the radio button, by searching for the radio
        button in the group with the given value and checking it.
        """
        if value is not None:
            value = ustr(value)
        found = False
        for el in self.el.xpath(
            "./ancestor-or-self::form[1]//input[@type='radio' and @name=$n]",
            n=self.el.attrib.get('name', '')
        ):
            if (el.attrib.get('value') == value):
                el.attrib['checked'] = ""
                found = True
            elif 'checked' in el.attrib:
                del el.attrib['checked']
        if value is not None and not found:
            raise AssertionError("Value %r not present"
                                 " in radio button group %r" %
                                 (value, self.el.attrib.get('name')))
        return self

    @when("textarea")  # NOQA
    def fill(self, value):
        """
        Set the value of a textarea control
        """
        if value is not None:
            value = ustr(value)
        self.el.text = value
        return self

    @when("input[@type='file']")  # NOQA
    def fill(self, value):
        """
        Set the value of a file input box
        """
        if value is None:
            try:
                del self.el.attrib['value']
            except KeyError:
                pass
        else:
            self.value = value
        return self

    @when("input")  # NOQA
    def fill(self, value):
        """
        Set the value of a (text, password, ...) input box
        """
        if value is None:
            try:
                del self.el.attrib['value']
            except KeyError:
                pass
        else:
            self.value = ustr(value)
        return self

    @when("select[@multiple]")  # NOQA
    def fill(self, values):
        """
        Set the values of a multiple select box

        :param values: list of values to be selected
        """
        options = self.el.xpath('.//option')
        if all(isinstance(v, bool) for v in values):
            values = [
                opt.attrib.get('value', opt.text)
                for selected, opt in zip(values, options)
            ]

        found = set()
        values = set(ustr(v) for v in values)
        for opt in options:
            value = opt.attrib.get('value', opt.text)
            if value in values:
                opt.attrib['selected'] = ""
                found.add(value)
            elif 'selected' in opt.attrib:
                del opt.attrib['selected']
        if found != values:
            raise AssertionError("Values %r not present in select %r" % (
                values - found,
                self.el.attrib.get('name'))
            )
        return self

    @when("select[not(@multiple)]")  # NOQA
    def fill(self, value):
        """
        Set the values of a multiple select box

        :param values: list of values to be selected
        """
        if value is not None:
            value = ustr(value)
        found = False
        for opt in self.el.xpath('.//option'):
            if opt.attrib.get('value', opt.text) == value:
                opt.attrib['selected'] = ""
                found = True
            elif 'selected' in opt.attrib:
                del opt.attrib['selected']
        if not found and value is not None:
            raise AssertionError("Value %r not present in select %r" %
                                 (value, self.el.attrib.get('name')))
        return self

    def html(self):
        """
        Return an HTML representation of the element

        :rtype: unicode string
        """
        return tostring(self.el, encoding='unicode')

    def pretty(self):
        """
        Return an pretty-printed string representation of the element

        :rtype: unicode string
        """
        return tostring(self.el, encoding='unicode', pretty_print=True)

    def striptags(self):
        r"""
        Strip tags out of the element and its children to leave only the
        textual content. Normalize all sequences of whitespace to a single
        space.

        Use this for simple text comparisons when testing for document content

        Example::

            >>> from fresco import Response
            >>> from flea import Agent
            >>> myapp = Response(['<p>the <span>foo</span> is'\
            ...                   ' completely <strong>b</strong>azzed</p>'])
            >>> agent = Agent(myapp).get('/')
            >>> agent['//p'].striptags()
            'the foo is completely bazzed'

        """
        def _striptags(node):
            if node.text:
                yield node.text
            for subnode in node:
                for text in _striptags(subnode):
                    yield text
                if subnode.tail:
                    yield subnode.tail
        return re.sub(r'\s\s*', ' ', ''.join(_striptags(self.el)))

    def __contains__(self, what):
        return what in self.html()


class ResultWrapper(list):
    """
    Wrap a list of elements (``ElementWrapper`` objects) returned from an xpath
    query, providing reasonable default behaviour for testing.

    ``ResultWrapper`` objects usually wrap ``ElementWrapper`` objects, which in
    turn wrap an lxml element and are normally created through the find/findcss
    methods of ``Agent``::

        >>> from fresco import Response
        >>> myapp = Response(['<html><p>item 1</p><p>item 2</p></html>'])
        >>> agent = Agent(myapp).get('/')
        >>> resultwrapper = agent.find('//p')

    ``ResultWrapper`` objects have list like behaviour::

        >>> len(resultwrapper)
        2
        >>> resultwrapper[0] #doctest: +ELLIPSIS
        <p>...</p>

    Attributes that are not part of the list interface are proxied to the first
    item in the result list for convenience. These two uses are equivalent::

        >>> resultwrapper[0].text
        'item 1'
        >>> resultwrapper.text
        'item 1'

    Items in the ``ResultWrapper`` are ``ElementWrapper`` instances, which
    provide methods in addition to the normal lxml.element methods (eg
    ``click()``, setting/getting form field values etc).

    """
    def __init__(self, elements, expr=None):
        super(ResultWrapper, self).__init__(elements)
        self.__dict__['expr'] = expr

    def __getattr__(self, attr):
        return getattr(self[0], attr)

    def __setattr__(self, attr, value):
        return setattr(self[0], attr, value)

    def __getitem__(self, item):
        try:
            if isinstance(item, int):
                return super(ResultWrapper, self).__getitem__(item)
            else:
                return self[0][item]
        except IndexError:
            raise IndexError("list index out of range for %r" % (self,))

    def __contains__(self, what):
        return self[0].__contains__(what)

    def __repr__(self):
        return "<ResultWrapper %r>" % (self.__dict__['expr'],)

    def filter_on_text(self, matcher):
        """
        Return a new :class:`ResultWrapper` of the elements in ``elements``
        where applying the function ``matcher`` to the text contained in
        the element results in a truth value.
        """
        return self.__class__(
            (e for e in self if matcher(e.striptags())),
            self.expr + " (filtered by %s)" % (matcher)
        )

    def filter(self, matcher):
        """
        Return a new :class:`ResultWrapper` of the elements in ``elements``
        where applying the function ``matcher`` to the element results in
        a truth value. """
        return self.__class__(
            (e for e in self if matcher(e)),
            self.expr + " (filtered by %s)" % (matcher)
        )


def guess_expression_flavor(expr):
    """
    Try to guess whether ``expr`` is a CSS selector or XPath expression.

    ``css`` is the default value returned for expressions valid in both
    syntaxes.
    """
    try:
        XPath(expr)
    except XPathError:
        return 'css'

    try:
        CSSSelector(expr)
    except (AssertionError, SelectorSyntaxError):
        return 'xpath'

    if '/' in expr:
        return 'xpath'
    if '@' in expr:
        return 'xpath'
    return 'css'
