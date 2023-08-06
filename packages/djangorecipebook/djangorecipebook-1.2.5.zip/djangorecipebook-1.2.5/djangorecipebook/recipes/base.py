"""
Defines the base recipe for all recipes of the recipe book
"""

import os
import re

from zc.recipe.egg import Egg


class BaseRecipe(object):

    def __init__(self, buildout, name, options):

        # recipe book's egg
        self.egg = Egg(buildout, options['recipe'].split(':')[0], options)

        self.buildout, self.name, self.options = buildout, name, options

        options['root_dir'] = self.buildout['buildout']['directory']

        # extraction of buildout parameters
        options['bin_dir'] = self.buildout['buildout']['bin-directory']
        options['part_dir'] = os.path.join(
            self.buildout['buildout']['parts-directory'],
            'djangorecipebook'
        )

        # extraction of common options
        proj_dir = options.get('project-dir', '.')
        options['proj_dir'] = os.path.normpath(
            os.path.join(options['root_dir'], proj_dir))
        options.setdefault('settings', 'settings')
        options.setdefault('initialization', '')

        extra_paths = [options['root_dir']]
        if proj_dir != '.':
            extra_paths.append(self.options['proj_dir'])
        for path in options.get('extra-paths', '').splitlines():
            path = path.strip()
            if path:
                extra_paths.append(os.path.normpath(path))
        options['extra-paths'] = ';'.join(extra_paths)

        options.setdefault('envvars', '')

        try:
            self.django_version = \
                tuple(map(int, self.buildout.versions['django'].split(".")))
        except KeyError:
            self.django_version = (999,)  # latest

    def _initialization(self):
        init = self.options['initialization']
        if self.options['envvars']:
            for kv in self.options['envvars'].splitlines():
                kv = kv.strip()
                try:
                    init += "\nos.environ['%s'] = '%s'" % \
                            tuple(re.split('\s*=\s*', kv))
                except TypeError:
                    raise ValueError('Invalid environment variable '
                                     'statement: "%s"' % kv)

        if init and not 'import os' in init:
            init = 'import os\n' + init

        return init

    def options_to_list(self, option):
        value = self.options.get(option, '')
        if value:
            return re.split('\s+', value)
        return []
