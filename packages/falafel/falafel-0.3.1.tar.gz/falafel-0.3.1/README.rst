==============
python-falafel
==============

testrunner (based on unittest package) suited for long-running unit/integration tests.

.. sidebar:: Links:

   * `Repository <https://github.com/thisch/python-falafel>`_ (at GitHub)
   * `Issue tracker <https://github.com/thisch/python-falafel/issues>`_ (at GitHub)
   * `Travis CI <https://travis-ci.org/#!/thisch/python-falafel>`_ |build-status|

.. |build-status|
   image:: https://secure.travis-ci.org/thisch/python-falafel.png?branch=master
   :target: http://travis-ci.org/thisch/python-falafel
   :alt: Build Status

Features:

* colorized testrunner output (using `redgreenunittests`)
* python loggers can be used in test classes
* colorized log message output
* output of each test can we redirected to logfiles
* tests can generate files and arbitrary data which is written to the logdirectory

TODO:

* xunit support
* different verbosity levels in testrunner output
* falafel script which parses a `.falafel.cfg` config file
