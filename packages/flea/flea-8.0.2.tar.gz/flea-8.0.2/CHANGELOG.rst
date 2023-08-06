Changes
---------

Version 8.0.2

* Bugfix: keys placed into the WSGI environment are no longer propagated
	between requests.

Version 8.0.1

* Bugfix: accessing the selected property of an <option> element no longer
	raises an exception. Thanks to Andrew Nelis for the patch.

Version 8.0

* Renamed flea.testagent.TestAgent to flea.agent.Agent. This avoids conflicting
  with the usual naming convention for test modules and classes.
* Test suite now uses py.test
* Fixed bug where the flea Agent would register a Fresco request object in the
  WSGI environ, preventing the application under test from later creating a
  custom request class instance

Version 7.5.0

* Changed licensing to the Apache License
* Internal refactoring to break into multiple modules (you will need to modify
  your import statements if you are importing anything other than
  flea.TestAgent)
* Added a ``TestAgent.environ`` property

Version 7.4.8

* Bugfix: options.selected property getter method had an erroneous argument

Version 7.4.7

* Fixed errors when running under python 3.2

Version 7.4.6

* Added a ``fill_sloppy`` method that doesn't raise an exception when fields
  don't exist

Version 7.4.5

* Bugfix: the order of inputs in a form is now respected in the submitted data
* Bugfix: improved handling of unicode values in ``form.fill()``
* Bugfix: TestAgent.reload now always replays the original WSGI environ dict
* Bugfix: mutations of the WSGI environ made by the application under test
  are no longer propagated between requests
* Bugfix: fixed exception raised when calling TestAgent.new_session()
* Added html, pretty, striptags and __contains__ convenience methods to the
  TestAgent object

Version 7.4.4

* Bugfix: cookies are now isolated between requests
* Bugfix: no longer raise an exception when called with an absolute url for the
  first request

Version 7.4.3

* Improvements to TestAgent.serve that make it possible to use through a proxy
  server

Version 7.4.2

* TestAgent.post now accepts data as a byte string (in addition to a dict or
  iterable)
* Added shortcut methods for other common HTTP methods: HEAD, PUT, PATCH and
  DELETE
* The ``environ_defaults`` dict is now persisted between instances. This is
  useful for setting default values that will be applied to all subsequent
  requests, eg::

  	agent = TestAgent(app)
  	agent.environ_defaults['REMOTE_ADDR'] = 'www.example.org'
  	agent.environ_defaults['REMOTE_USER'] = 'alice'

Version 7.4.1

* Bugfix: Fixed error in TestAgent.serve()
* Improved unicode handling for WSGI environ values

Version 7.4.0

* Switch to fresco from pesto
* Experimental Python 3 support
* Bugfix: ensure WSGI response iterator's close method is always called

Version 7.3.6

* Bugfix for broken TestAgent.serve

* Improvements to TestAgent.serve that make it possible to use through a proxy
  server

Version 7.3.5

* Backported changes and fixes from version 7.4.2, with the exception of Python
  3 support and support for fresco. See notes above for the changes in this
  version.

Version 7.3.4

* Updated setup.py to require cssselect

Version 7.3.3

* Included logging facility to allow easy tracing of calls to the application
  under test

* Added a ``flea.testing`` WSGI environ key so that the AUT can tell when it is
  running in a test environment

* Fixed a bug in post_multipart that caused an error when passing a data dict

Version 7.3.2

* Fixed bug in ``fill`` method, which was not clearing checkbox elements

Version 7.3.1

* Fixed bug in TestAgent.follow

Version 7.3.0

* New API for form filling, with each control type having a ``fill`` method. The ``value`` attribute is no longer overloaded.

* You can now traverse the DOM by calling the TestAgent object directly with either a CSS selector or XPath expression.

* TestAgent.click() now takes an argument that selects links by their textual
  content, eg ``agent.click('view results')``. If you want the old behaviour,
  you need to pass a second argument, eg ``agent.click('//a[.="view results"]',
  'xpath')``.

Version 7.2.1

* The value property now does the right thing with respect to checkbox and
	radio groups. For checkbox groups, ``.value`` will get/set a list of values
	corresponding to the selected checkboxes. For radio buttons, ``.value`` will
	get/set the selected radio button.

* Fixed error following links containing a fragment identifier

Version 7.2.0

* Added .reload and .new_session methods to TestAgent

Version 7.1.1

* Fixed check_status argument not being accepted in get, post, click, submit
  etc methods

Version 7.1.0

* Added .fill - fill multiple form fields in a single call.

* Added .show - show the current response in a web browser

* Added .serve - start an HTTP server for the the application under test and
	open a browser at the current page

* Added check for HTTP status success or redirect codes (2xx or 3xx),
	anything else raises an AssertionError by default

* Changed default behaviour to follow HTTP redirects

* Changed version numbering scheme to <major>.<minor>

Version 7

* Fixed error when accessing the 'checked' property of an input box

* Prevented raising of ValueError on non-matching xpaths when accessed by
	``.find()`` (``__getitem__`` will however still raise an error).

Version 6

* Requires pesto 16 or higher

Version 5

* Updated setup.py for compatibility with pesto==15

Version 4

* Added support for file upload fields

* Allow TestAgent.get/post etc to take a relative URI as an argument

Version 3

* Updated setup.py for compatibility with pesto==14

Version 2

* EXSLT regular expression namespace is bound to ``re`` prefix by default,
	allowing regexps in xpath expressions.

* Bug fixes for form element handling

Version 1

* Initial release

