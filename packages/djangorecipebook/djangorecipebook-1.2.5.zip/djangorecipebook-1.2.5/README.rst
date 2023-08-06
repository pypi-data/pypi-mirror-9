djangorecipebook
================

|copyright| 2014 Thomas Khyn

Buildout recipes for django development


About
-----

The recipes available in djangorecipebook are mostly derived from
djangorecipe_'s functionalities. However, while djangorecipe aims at generating
all scripts in one part, djangorecipebook enables you to define one part per
script (create, manage, wsgi, test, makemigrations), hence allowing the use of
different settings and/or eggs for each part.

Through its automatic minimal settings generation, djangorecipebook is
particularly adapted to reusable apps development, e.g. for testing or
generating migrations with `Django 1.7+`_, south_ or both.

djangorecipebook works with django 1.4 to 1.8 and relevant python versions
(2.6 to 3.4, depending on django version).


Available recipes
-----------------

djangorecipebook:manage
   Creates a management script for the project

djangorecipebook:wsgi
   Creates a wsgi script for the project

djangorecipebook:fcgi
   Creates a fcgi script for the project

djangorecipebook:test
   Creates a script that invokes ``manage.py test [apps]``.

djangorecipebook:makemigrations (new in v1.2)
   Generates south_ and/or Django 1.7+ migrations

djangorecipebook:migrate (new in v1.2)
   Invokes ``manage.py migrate [apps]``. For the lazy ones.

djangorecipebook:create
   Creates a django project from a user-defined template or using django's
   ``startproject`` management command. This recipe will not generate any
   script. The name of the created project is the name of the section.


Options
-------

Common options
..............

project-dir
   The directory where the project files lie, relative to the buildout.cfg
   directory.

   Defaults to ``'.'`` (buildout directory).

settings
   The settings module to load, imported from the project directory.

   Defaults to ``'settings'`` or a set of minimal settings, depending on the
   recipe.

extra-paths
   Paths to add to sys.path in the generated script.

   Defaults to ``[]``.

envvars
   Any environment variable that need to be set for the test run, one per line,
   under the form ``VARIABLE = value`` (spaces are tolerated).

   Defaults to no environment variable set.

initialization
   Some (basic) python initialization code to insert in the generated script.
   Don't forget that leading whitespaces are stripped.

   Defaults to ``''``.


Manage options
..............

settings
   If a settings module is not provided, the settings will be a set of minimal
   parameters, with the added installed apps below.

   Defaults to minimal settings.

inst_apps
   The apps to add to the ``INSTALLED_APPS`` setting if no settings module is
   provided. This option should not be used when a settings module is provided.

   Defaults to ``''``.

args
   Any command-line argument you wish to have added to the generated script,
   separated by spaces or line-breaks.

   Defaults to no arguments.


WSGI and FCGI options
.....................

settings
   Must be a settings module, no default minimal settings are available for
   wsgi and fcgi recipes.

log-file
   The path to a log file where all stdout and/or stderr data should be
   redirected to.

   Defaults to ``''``, which disables logging

log-level
   The level to log errors for. Can be one of INFO (stdout + stderr) or
   ERROR (stderr only).

   Defaults to ``INFO``.

virtualenv
   The virtualenv that should be used to run the wsgi/fcgi script. This
   requires virtualenv **and** virtualenvwrapper, as it relies upon the
   ``WORKON_HOME`` environment variable.

   Defaults to ``''``, which disables any virtual environment setup.

script_path
   The desired output path of the script, as a path to a filename relative to
   the buildout directory (= where the ``buildout.cfg`` file lies).

   Defaults to buildout's bin directory with the recipe's name.

application (wsgi only)
   The path to a user-defined wsgi application.

   Defaults to the result of django's ``get_wsgi_application()``

Test options
............

settings, inst_apps, args
   See `Manage options`_.

nose
   Use this option if you are using nose_ (and therefore django_nose_) to test
   your Django app or project. This will simply include ``django_nose`` and
   ``nose`` in your buildout.

   Defaults to unset.

apps
   The names of the apps that should be tested, separated by spaces or
   line-breaks. If using minimal settings, these apps will be added to the
   ``INSTALLED_APPS`` (in addition to those in the ``inst_apps`` option).

   Defaults to ``''``, all the apps in ``INSTALLED_APPS``


Makemigrations options
......................

settings, inst_apps, args
   See `Manage options`_.

apps
   The names of the apps for which migrations should be generated, separated
   by spaces or line-breaks. If using minimal settings, these apps will be
   added to the ``INSTALLED_APPS`` (in addition to those in the ``inst_apps``
   option).

   Defaults to ``''``, all the apps in ``INSTALLED_APPS``

south
   If this option has a value, south_ migrations will also be generated when
   using Django 1.7+ (behind the scenes, djangorecipebook installs django 1.6.x
   and south distributions and links them in a separate script that can be
   found in the parts/djangorecipeboook directory). This option has no effect
   with Django < 1.7, where ``south`` migrations will always be generated and
   ``south`` will always be installed if you are using this recipe.

   Defaults to ``undefined`` (no south migrations generation).


The ``makemigrations`` recipe will generate:

- Django 1.7+ migrations if you are using Django 1.7+
- and/or south_ migrations if:
   - you are using Django 1.7+ and provide a value for the ``south`` option
   - or you are using Django < 1.7, whatever the value of the ``south`` option

When generating south migrations, the ``--initial`` flag can be provided when
invoking the script from the command line. ``--initial`` has no effect
whatsoever on Django 1.7+ migrations.

Additionally, djangorecipebook will detect the apps where south migrations must
be initialised, and automatically add the ``--auto``. That means you do not
have to worry anymore about providing ``--auto`` or ``--initial`` flags.

If you are using Django 1.7+ and have south_ migrations in the
``app.migrations`` package, djangorecipebook will automatically rename this
existing package to ``app.south_migrations`` and place the Django 1.7+
migrations in ``app.migrations``. From south 1.0.0, south migrations placed
in the ``south_migrations`` module are detected.


Migrate options
...............

Same options as in `Test options`_. The only difference is that you cannot use
minimal settings (the default is ``'settings'``) nor the ``inst_apps`` option.
Indeed, migrations generally need a database to migrate!


Create options
..............

In create mode, the following common options are unused:

- extra-paths
- initialization

The settings import path must be set as it is used to determine whether the
project has already been created or not.

The following options are added:

template-dirs
   The directories in which to search for user-defined project templates. This
   option may also be added in a ``[djangorecipebook]`` section (for example in
   the default.cfg file). See the `Templates discovery`_ section below.

   Defaults to the built-in templates directory, containing default django
   project templates.

template
   The template that should be used.

   Defaults to the standard django project for the major version of django you
   are using.

secret
   The ``SECRET_KEY`` to be used in the created settings file(s).

   Defaults to a randomly generated alphanumeric key.

For more details on templating, see the `Templates`_ section below.


Templates
---------

In create mode, a templating engine is available for greater personalisation
of your django project initialization.

Templates discovery
...................

If a `template-dirs` option is found either in the recipe section or in a
specific `djangorecipebook` section, the recipe searches in these directories
- from the last defined to the first - for a subdirectory name matching the
`template` name provided.

If the search is unsuccessful or if none of `template-dirs` or `template` are
defined, the recipe uses the default template for the major version of django
being used.

For example, if in ~/.buildout/default.cfg you have the following lines::

    [djangorecipebook]
    template-dirs =
      /my/project/template/directory
      /my/project/template/directory2

And your buildout.cfg contains this section::

    [mynewproject]
    recipe = djangorecipebook:create
    template-dirs = /my/other/template/dir
    template = mytemplate

The recipe will search for a ``mytemplate`` directory in that order:

1. /my/other/template/dir
2. /my/project/template/directory2
3. /my/project/template/directory

Template engine
...............

The template engine is as simple as it can be and relies upon pythons's
``string.Template``. A variable can be inserted in any file or directory name or
file content in template directory using the syntax ``${variable}``.

The following variables are available:

- any user-defined recipe option from the configuration file
- ``secret``: the secret key for django settings
- ``project_name``: the project name (= the section name)
- ``year``: the current year
- ``month``: the current month
- ``day``: the current day of the month

For example, if you have in buildout.cfg::

    [mynewproject]
    recipe = djangorecipebook:create
    template = mytemplate
    author = Thomas Khyn

for a copyright notice in a module docstring, you may use::

    (c) ${year} ${author}

which will produce to the following output in the final file (if we are in
2014)::

    (c) 2014 Thomas Khyn

or, if you have a directory named ``${project_name}_parameters``, the final name
will be ``mynewproject_parameters``.


.. |copyright| unicode:: 0xA9
.. _djangorecipe: https://github.com/rvanlaar/djangorecipe
.. _nose: http://nose.readthedocs.org/en/latest/
.. _django_nose: https://pypi.python.org/pypi/django-nose
.. _south: http://south.readthedocs.org
.. _`Django 1.7+`: https://docs.djangoproject.com/en/dev/topics/migrations/
