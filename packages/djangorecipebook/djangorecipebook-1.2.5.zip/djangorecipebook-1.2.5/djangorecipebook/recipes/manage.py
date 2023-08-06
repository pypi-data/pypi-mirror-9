"""
Recipe generating a management script
"""

import sys

from zc.buildout import easy_install

from .base import BaseRecipe
from ..exceptions import ImproperlyConfigured


class Recipe(BaseRecipe):

    def _packages(self):
        return ['djangorecipebook']

    def __init__(self, buildout, name, options):
        options.setdefault('settings', '')
        super(Recipe, self).__init__(buildout, name, options)
        options.setdefault('args', '')

        inst_apps = options.setdefault('inst_apps', '')
        apps = options.get('apps', '')
        self.added_settings = {}
        if inst_apps or apps:
            inst_apps = self.options_to_list('inst_apps')
            apps = self.options_to_list('apps')
            inst_apps.extend(set(apps).difference(inst_apps))
            self.added_settings['INSTALLED_APPS'] = tuple(inst_apps)

    @property
    def script_path(self):
        return self.__class__.__module__.replace('recipes', 'scripts')

    def _arguments(self):
        """
        Returns the list of arguments for the djangorecipebook script
        """
        args = ''
        for arg in self.options_to_list('args'):
            args += ", '%s'" % arg

        settings = self.options['settings']
        if settings:
            settings = "'%s'" % settings
        else:
            settings = 'added_settings'  # see self._initialization

        return "%s%s" % (settings, args)

    def _initialization(self):
        init = super(Recipe, self)._initialization()

        if not self.options['settings']:
            init += '\n\nadded_settings = %s' % repr(self.added_settings)

        return init

    def install(self):
        if self.options['settings'] and self.options['inst_apps']:
            raise ImproperlyConfigured(
                'Cannot define a settings module and a list of installed apps')

        __, working_set = self.egg.working_set(self._packages())
        return easy_install.scripts(
            [(self.name, self.script_path, 'main')],
            working_set, sys.executable, self.options['bin_dir'],
            extra_paths=self.options['extra-paths'].split(';'),
            arguments=self._arguments(),
            initialization=self._initialization())

    def update(self):
        self.install()


class AppsRecipe(Recipe):
    """
    A management recipe with an 'apps' option
    """

    def __init__(self, buildout, name, options):
        options.setdefault('apps', '')
        super(AppsRecipe, self).__init__(buildout, name, options)

    def _arguments(self):
        args = super(AppsRecipe, self)._arguments()
        for app in self.options_to_list('apps'):
            args += ", '%s'" % app
        return args
