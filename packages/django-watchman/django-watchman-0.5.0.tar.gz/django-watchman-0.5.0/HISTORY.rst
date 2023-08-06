.. :changelog:

History
-------
0.5.0 (2015-01-25)
++++++++++++++++++

* Add ``watchman`` management command
 * Exit code of ``0`` if all checks pass, ``1`` otherwise
 * Print json stacktrace to ``stderr`` if check fails
 * Handles ``--verbosity`` option to print all status checks
 * ``-c``, ``--checks``, ``-s``, ``--skips`` options take comma-separated list of python paths to run / skip
* Improve identifiability of emails sent from a django-watchman endpoint
 * From: watchman@example.com
 * Subject: django-watchman email check
 * Body: This is an automated test of the email system.
 * Add ``X-DJANGO-WATCHMAN: True`` custom header
* Add new default check: ``storage`` check
 * Checks that files can be both written and read with the current Django storage engine
 * Add ``WATCHMAN_ENABLE_PAID_CHECKS`` setting to enable all paid checks without modifying ``WATCHMAN_CHECKS``
* Remove ``email_status`` from default checks
* Refactor ``utils.get_checks`` to allow reuse in management command
 * ``get_checks`` now performs the optional check inclusion / skipping
 * ``status`` refactored to pull ``check_list`` / ``skip_list`` from GET params and pass them to ``get_checks``
* Namespace cache keys
* Update documentation

0.4.0 (2014-09-08)
++++++++++++++++++

* Add the ability to skip certain checks by passing one or more
  ``skip=path.to.callable`` GET params when hitting the watchman URL

0.3.0 (2014-09-05)
++++++++++++++++++

* New check - email (``watchman.checks.email_status``)! django-watchman will now
  check that your email settings are working too!
* Fix a few small issues in the readme
* Rearrange some of the code in checks.py

0.2.2 (2014-09-05)
++++++++++++++++++

* Fix and run tests on Python 2.7 and 3.4
* Bump django-jsonview dependency to latest
* Update tox envlist and travis config to test 2.7 / 3.4

0.2.1 (2014-09-04)
++++++++++++++++++

* Initialize django during tests to prevent app loading issue for Django >= 1.7
* Suppress ``MIDDLEWARE_CLASSES`` warning for Django >= 1.7
* Reorganize test imports
* Fix ``make test``, ``make coverage``, ``make release`` commands
* Add htmlcov/ directory to .gitignore
* Test django 1.4, 1.6, 1.7

0.2.0 (2014-09-04)
++++++++++++++++++

* Custom checks can now be written and run using the ``WATCHMAN_CHECKS`` setting
* A subset of the available checks can be run by passing the ``check`` GET param
  when hitting the watchman url

0.1.2 (2014-02-21)
++++++++++++++++++

* Move package requirements out of requirements.txt and into setup.py

0.1.1 (2014-02-09)
++++++++++++++++++

* Remove ``django>=1.5.5`` version specification
* Remove ``wheel`` requirement


0.1.0 (2014-02-08)
++++++++++++++++++

* First release on PyPI.
