1.0.0b1
-------

released 2012-03-20

Major changes afoot!

* Run your tests multiprocess!
* Nosedjango now has a plugin system including the following plugins:

  * Multiprocess support
  * Selenium
  * Cherrpy test server
  * Temporary file storage for testing
  * Celery
  * Sphinx Search
  * In-memory sqlite
  * SSH tunneling

* All of your testcases that use fixtures are now much faster.
  We use an improved transaction rollback strategy which optimizes away the
  slowest part of your testcase (loading fixtures).

0.8.1
-----

A bugfix release, released 2010-08-20

* Fix transaction management problems when using django.test.TestCase

0.8.0
-----

Un-debianized version, released 2010-08-18

* Add CHANGES (this!) file
* Remove debianization

0.7.3
-----

A bugfix release, released 2010-08-17

* debian: Don't package with cdbs
* Fix a bug caused by a merge

0.7.2
-----

A bugfix release, released 2010-02-25

* Add --django-interactive option to run tests interactively
* Fixed attribute error when transaction support is not supported by
  the database
* Add support for south
* Add a command-line option to run the tests using an in-memory sqlite
* Improve documentation
* Fix database and mail handling
* Clean up useless comments and code

0.7.1
-----

* Improve documentation on fixtures and transactiosn
* Allow transactiosn to be controlled per test

0.7.0
-----

* Add support for testing inside transactions
* Debianize nosedjango
* Improve documentation
