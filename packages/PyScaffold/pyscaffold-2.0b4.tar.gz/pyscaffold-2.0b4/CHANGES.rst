=============
Release Notes
=============

Version 2.0, 2015-??-??
=======================

- Split configuration and logic into setup.cfg and setup.py
- Removed .pre from version string (newer PEP 440)
- FIX: Sphinx now works if package name does not equal project name
- Allow namespace packages with --with-namespace
- Added a skeleton.py as a console_script template
- Set `v0.0` as initial tag to support PEP440 version inference
- Integration of the Versioneer functionality into setup.py

Version 1.4, 2014-12-16
=======================

- Added numpydoc flag --with-numpydoc
- Fix: Add django to requirements if --with-django
- Fix: Don't overwrite index.rst during update

Version 1.3.2, 2014-12-02
=========================

- Fix: path of Travis install script

Version 1.3.1, 2014-11-24
=========================

- Fix: --with-tox tuple bug #28

Version 1.3, 2014-11-17
=======================

- Support for Tox (https://tox.readthedocs.org/)
- flake8: exclude some files
- Usage of UTF8 as file encoding
- Fix: create non-existent files during update
- Fix: unit tests on MacOS
- Fix: unit tests on Windows
- Fix: Correct version when doing setup.py install

Version 1.2, 2014-10-13
=======================

- Support pre-commit hooks (http://pre-commit.com/)

Version 1.1, 2014-09-29
=======================

- Changed COPYING to LICENSE
- Support for all licenses from http://choosealicense.com/
- Fix: Allow update of license again
- Update to Versioneer 0.12

Version 1.0, 2014-09-05
=======================

- Fix when overwritten project has a git repository
- Documentation updates
- License section in Sphinx
- Django project support with --with-django flag
- Travis project support with --with-travis flag
- Replaced sh with own implementation
- Fix: new `git describe` version to PEP440 conversion
- conf.py improvements
- Added source code documentation
- Fix: Some Python 2/3 compatibility issues
- Support for Windows
- Dropped Python 2.6 support
- Some classifier updates

Version 0.9, 2014-07-27
=======================

- Documentation updates due to RTD
- Added a --force flag
- Some cleanups in setup.py

Version 0.8, 2014-07-25
=======================

- Update to Versioneer 0.10
- Moved sphinx-apidoc from setup.py to conf.py
- Better support for `make html`

Version 0.7, 2014-06-05
=======================

- Added Python 3.4 tests and support
- Flag --update updates only some files now
- Usage of setup_requires instead of six code

Version 0.6.1, 2014-05-15
=========================

- Fix: Removed six dependency in setup.py

Version 0.6, 2014-05-14
=======================

- Better usage of six
- Return non-zero exit status when doctests fail
- Updated README
- Fixes in Sphinx Makefile

Version 0.5, 2014-05-02
=======================

- Simplified some Travis tests
- Nicer output in case of errors
- Updated PyScaffold's own setup.py
- Added --junit_xml and --coverage_xml/html option
- Updated .gitignore file

Version 0.4.1, 2014-04-27
=========================

- Problem fixed with pytest-cov installation

Version 0.4, 2014-04-23
=======================

- PEP8 and PyFlakes fixes
- Added --version flag
- Small fixes and cleanups

Version 0.3, 2014-04-18
=======================

- PEP8 fixes
- More documentation
- Added update feature
- Fixes in setup.py

Version 0.2, 2014-04-15
=======================

- Checks when creating the project
- Fixes in COPYING
- Usage of sh instead of GitPython
- PEP8 fixes
- Python 3 compatibility
- Coverage with Coverall.io
- Some more unittests

Version 0.1.2, 2014-04-10
=========================

- Bugfix in Manifest.in
- Python 2.6 problems fixed

Version 0.1.1, 2014-04-10
=========================

- Unittesting with Travis
- Switch to string.Template
- Minor bugfixes

Version 0.1, 2014-04-03
=======================

- First release
