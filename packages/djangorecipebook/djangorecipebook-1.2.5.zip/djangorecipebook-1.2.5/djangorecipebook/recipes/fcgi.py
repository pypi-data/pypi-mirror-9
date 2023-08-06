"""
Base recipe for production scripts generation
"""

import os
import sys
import logging

from .base import BaseRecipe
from zc.buildout import easy_install


venv_setup = '''
activate_this = r'%s'
execfile(activate_this, dict(__file__=activate_this))
'''


class Recipe(BaseRecipe):

    script_template = ''

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        options.setdefault('log-file', '')

        if options['log-file']:
            loglevel = options.get('log-level', 'INFO')
            if loglevel not in ('INFO', 'ERROR'):
                raise ValueError('log-level should be INFO or ERROR')
            options['log-level'] = str(getattr(logging, loglevel))

        options.setdefault('virtualenv', '')
        options.setdefault('script_path', '')

    def _arguments(self):
        if self.options['log-file']:
            logfile = (", logfile='%s'" % self.options['log-file'])
            loglevel = (", level=%s" % self.options['log-level'])
        else:
            logfile = loglevel = ''

        return "'%s'%s%s" % (self.options['settings'], logfile, loglevel)

    def install(self):
        __, working_set = self.egg.working_set(['djangorecipebook'])

        venv = self.options['virtualenv']
        venv_path = ''

        if venv:
            workon_home = os.environ.get('WORKON_HOME', '')
            if workon_home:
                envs = os.listdir(workon_home)
                if venv in envs:
                    bin_dir = 'Scripts' if sys.platform == 'win32' else 'bin'
                    venv_path = os.path.join(workon_home, venv,
                                             bin_dir, 'activate_this.py')
                    if not os.path.isfile(venv_path):
                        logging.getLogger(self.name).error(
                            "part [%s], option virtualenv: activate_this.py "
                            "was not found in %s." %
                            (self.name, os.path.dirname(venv_path)))
                else:
                    logging.getLogger(self.name).error(
                        "part [%s]: no virtualenv named '%s' is available on "
                        "this system. Please create it or update the "
                        "virtualenv option." % (self.name, venv))
            else:
                logging.getLogger(self.name).error(
                    "The 'virtualenv' option is set in part [%(part)s] while "
                    "no WORKON_HOME environment variable is available. "
                    "Part [%(part)s] will be installed in the global python "
                    "environment." % {'part': self.name})

        _script_template = easy_install.script_template
        easy_install.script_template = easy_install.script_header + \
            ((venv_setup % venv_path) if venv_path else '') + \
            (self.script_template if self.script_template
                else _script_template.split('\n', 1)[1])
            # we use split to strip the 1st line of _script_template, which
            # is the header

        if self.options['script_path']:
            dest = os.path.normpath(os.path.join(self.options['root_dir'],
                                                 self.options['script_path']))
            dest_dir, dest_name = os.path.split(dest)
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)
        else:
            dest_dir = self.options['bin_dir']
            dest_name = self.name

        module_name = self.__class__.__module__.replace('recipes', 'scripts')
        script = easy_install.scripts(
            [(dest_name, module_name, 'main')],
            working_set, sys.executable, dest_dir,
            extra_paths=self.options['extra-paths'].split(';'),
            arguments=self._arguments(),
            initialization=self._initialization())

        easy_install.script_template = _script_template

        if self.options['script_path'] and sys.platform == 'win32':
            # on windows, the xxx-script.py must be renamed and the .exe
            # deleted if the script path is provided
            for s in script:
                if s.endswith('.py'):
                    # we rename the .py file, deleting the existing one if any
                    if os.path.exists(dest):
                        os.remove(dest)
                    os.rename(s, dest)
                else:
                    # we remove the .exe file
                    os.remove(s)
            script = [dest]

        return script

    def update(self):
        self.install()
