django-nose-qunit README
========================

Integrate QUnit JavaScript tests into a Django test suite via nose.

Installation
------------

1. ``pip install django-nose-qunit``.
2. Add ``'django_nose_qunit'`` to your ``INSTALLED_APPS`` setting.
3. Ensure that you're using nose as your test runner by using the following
   Django setting ::

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

4. Enable the nose plugin by adding it to the ``NOSE_PLUGINS`` Django setting::

        NOSE_PLUGINS = [
            'django_nose_qunit.QUnitPlugin'
        ]

5. Add an entry to your URL configuration::

        from django_nose_qunit.urls import urlpatterns as qunit_urlpatterns
        urlpatterns += qunit_urlpatterns

   This adds new URLs of the form ``/qunit/*``, and they return a 404
   unless ``DEBUG`` is True or QUnit tests have been initialized as part of a
   test run.
6. Configure Selenium as explained in the
   `sbo-selenium <https://github.com/safarijv/sbo-selenium>`_ README.
7. Make sure ``MEDIA_URL`` is set to some non-empty string, like "/media/".
   If this is not done, the live test server can occasionally get confused and
   treat requests for a test page as requests for static files.

Creating Unit Tests
-------------------

Tests can be written in JavaScript using QUnit as normal; see the
`QUnit documentation <http://qunitjs.com/>`_ for details.  You need only create a
JavaScript file, not the HTML page that will load it (that is provided by the
template at ``qunit/template.html``).  If your tests depend on HTML fixtures in the
qunit-fixture div, create those as HTML fragments in files which can be loaded
as templates.  External script dependencies should be files in the staticfiles
load path.  You should add ``QUnit.Django.start();`` before your test definitions
and ``QUnit.Django.end();`` at the end of your test definitions; this allows the
tests to start executing at an appropriate time depending on whether they're
running in a browser, in a nose test run, or inside a require() block of an AMD
loader like `RequireJS <http://requirejs.org/>`_.

To make nose aware of your QUnit tests, create a subclass of
``django_nose_qunit.QUnitTestCase`` in a file which would normally be searched by
nose, for example ``my_app/test/qunit/test_case.py``.  It can contain as little as
just the ``test_file`` attribute (a path to a QUnit test script, relative to
``STATIC_URL``).  Any script dependencies for your test script should be given
as paths relative to ``STATIC_URL`` in the ``dependencies`` attribute.  Paths to
HTML fixture templates are listed in the ``html_fixtures`` attribute.

Running Unit Tests
------------------
Add ``--with-django-qunit`` to your normal test execution command (using
django-admin.py or manage.py).  Execution can be restricted to one or more
specified packages and/or classes as normal ("myapp", "myapp.tests.qunit",
"myapp.tests.qunit:MyTestCase", etc.).  There is currently no support for
running only a single module or test within a QUnit test script; QUnit module
and test names can be arbitrary strings, which makes it difficult for the nose
command line parser to handle them.

To run the QUnit tests in a regular web browser, use the runserver management
command with ``QUNIT_DYNAMIC_REGISTRY`` set to True (by default, it has the same
value as ``DEBUG``).  If ``DEBUG`` is False, you'll also need to use the ``--insecure``
parameter to serve static files.  You can then access a list of links to the
available QUnit tests at a URL like http://localhost:8000/qunit/.  This can be
useful when first developing a test script and when troubleshooting failing
tests.

How It Works
------------
QUnitTestCase is a subclass of Django's ``LiveServerTestCase``, which starts a
Django test server in the background on setup of the test class and stops it on
teardown.  django_nose_qunit includes a nose plugin which can accommodate tests
written as simple wrappers for JavaScript test files.  When nose searches for
tests to run, the plugin tells it how to ask a browser via Selenium WebDriver
to load each test script (without running the tests) in order to get
information about the modules and tests it contains.  Once these tests are
enumerated, they are run like any other test case.  The first execution of
a test from a QUnit test script runs all of the tests in the script, and the
results are stored.  Each test case then reports success or failure based on
the reported results, with failures including any messages provided by QUnit.
