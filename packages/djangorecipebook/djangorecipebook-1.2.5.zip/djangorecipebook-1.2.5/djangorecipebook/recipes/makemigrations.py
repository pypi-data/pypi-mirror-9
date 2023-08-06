"""
Recipe generating a script to generate migrations
"""

import os
import sys

from zc.buildout import easy_install


from .manage import AppsRecipe
from ..exceptions import ImproperlyConfigured


class Recipe(AppsRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)

        self.dj17plus = self.django_version >= (1, 7)
        self.south = 'south' in options
        self.dj16script = None

    def _packages(self):
        pkgs = ['djangorecipebook']
        if not self.dj17plus:
            pkgs.append('djangorecipebook[south]')
        return pkgs

    def install(self):
        if not any((self.options['settings'], self.options['inst_apps'],
                    self.options['apps'])):
            raise ImproperlyConfigured(
                'You need to provide at least one installed app or a settings '
                'module to generate migrations.')

        if self.dj17plus and self.south:
            # we need dual migrations generation, so we need to install
            # a second script with django 1.6 and return its path

            # tweak the installer's version
            versions = easy_install.Installer._versions
            versions['django'] = '<1.7'

            if not os.path.isdir(self.options['part_dir']):
                os.makedirs(self.options['part_dir'])

            name = 'dj16south_schemamigration'

            __, working_set = self.egg.working_set(self._packages() +
                                                   ['djangorecipebook[south]'])
            easy_install.scripts(
                [(name, self.script_path, 'make_south_from_dj17')],
                working_set, sys.executable, self.options['part_dir'],
                extra_paths=self.options['extra-paths'].split(';'),
                arguments=super(Recipe, self)._arguments(),
                initialization=self._initialization())

            try:
                versions['django'] = self.buildout.versions['django']
            except KeyError:  # no django version specified
                del versions['django']

            # we store the script path to invoke the main script
            self.dj16script = repr(os.path.join(self.options['part_dir'],
                                                name))

            # no need to notify the user about picking a django < 1.7 version
            easy_install.Installer._picked_versions.pop('django', None)

        return super(Recipe, self).install()

    def _arguments(self):
        """
        Adds the apps to the arguments
        """
        args = super(Recipe, self)._arguments()

        if self.dj16script:
            args += ", dj16script=%s" % self.dj16script

        return args
