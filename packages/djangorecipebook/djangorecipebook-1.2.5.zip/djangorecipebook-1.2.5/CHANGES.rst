Changes
=======



1.2 (22-11-2014)
----------------

- Django 1.7 is now the officially supported Django release
- Added ``makemigrations`` recipe that supports Django 1.7 and south migrations
- Added ``migrate`` recipe

1.2.1 (25-11-2014)
..................

- Fixed template directory bug in create recipe
- Fixed ``makemigrations`` recipe for dual migrations generation

1.2.2 (30-11-2014)
..................

- Added ``application`` option to ``wsgi`` recipe
- Added ``script_path`` option to ``fcgi`` and ``wsgi`` recipes

1.2.3 (30-11-2014)
..................

- Fixed ``script_path`` option edge-cases bugs

1.2.4 (12-12-2014)
..................

- Fixed fcgi/wsgi existing script file issue on windows

1.2.5 (14-04-2015)
..................

- Added Django 1.8 support


1.1 (03-08-2014)
----------------

- Added ``nose`` and ``workingdir`` options to ``test`` recipe, to install
  and run with django_nose_ and select the base directory for the test modules
- Added ``args`` option to ``manage`` and ``test`` recipes to provide
  supplementary command line arguments
- Added ``envvar`` option to all recipes to set environment variables

1.1.1 (08-10-2014)
..................

- Fixed bug when calling manage script with a django command


1.0 (02-08-2014)
----------------

- Supports Django 1.4 to 1.7, and relevant python versions (2.6 to 3.4)


0.2.1 (20-07-2014)
------------------

- Added virtualenv option in wsgi recipe
- Added fcgi recipe
- Fixed settings issue when using --settings argument


0.2 (08-04-2014)
----------------

- Added create recipe and templating engine
- Added bootstrap.py
- Removed script-name option (from docs, as it was not implemented)


0.1 (05-04-2014)
----------------

- Initial version. Manage, test and wsgi recipes implemented

0.0 (04-04-2014)
----------------

- Birth


.. _django_nose: https://pypi.python.org/pypi/django-nose
