"""
Django project initialization recipe
"""

import os
import sys
import shutil
import logging
import tempfile
from random import choice
from datetime import date

from .base import BaseRecipe

from djangorecipebook import templating


class Recipe(BaseRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)

        options.setdefault('template', '')

        temp_dirs_str = []
        bo_options = buildout.get('djangorecipebook', None)
        if bo_options:
            bo_dirs = bo_options.get('template-dirs', None)
            if bo_dirs:
                temp_dirs_str.append(bo_dirs)
        recipe_options = options.get('template-dirs', None)
        if recipe_options:
            temp_dirs_str.append(recipe_options)

        temp_dirs = []
        for s in temp_dirs_str:
            for path in s.splitlines():
                path = path.strip()
                if path:
                    temp_dirs.append(os.path.normpath(path))

        temp_dirs.reverse()
        options['template-dirs'] = ';'.join(temp_dirs)

    def install(self):
        # creates the project if it does not exist yet
        # the existence test relies on the existence of the settings module
        settings_path = \
            os.path.join(self.options['proj_dir'],
                         *self.options['settings'].split('.'))
        if not (os.path.exists(settings_path + '.py')):
            self.create_project()
        else:
            logging.getLogger(self.name).warning(
                'Skipped creation of project %s since its main settings ' \
                'module exists' % self.name)
        return ()  # nothing should be removed on uninstall

    def get_random_secret(self):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join([choice(chars) for i in range(50)])

    def get_context(self):
        today = date.today()
        context = {
            'secret': self.options.get('secret', self.get_random_secret()),
            'project_name': self.name,
            'year': today.year,
            'month': today.month,
            'day': today.day,
        }
        context.update(self.options)
        return context

    def create_project(self):
        # create the project directory if it does not exist
        if not os.path.exists(self.options['proj_dir']):
            os.makedirs(self.options['proj_dir'])

        temp_path = False
        if self.options['template'] and self.options['template-dirs']:
            # the user provided a template to load

            # look for a template in the template directories provided
            # (self.template_dirs is already in reverse order)
            for d in self.options['template-dirs'].split(';'):
                d = os.path.abspath(d)
                if self.options['template'] in os.listdir(d):
                    # we have a template candidate, load it
                    temp_path = os.path.join(d, self.options['template'])
                    break

        if temp_path:
            # prepare templating engine
            context = self.get_context()

            # copy files and run templating engine
            for sub in os.listdir(temp_path):
                src_path = os.path.join(temp_path, sub)
                tgt_path = os.path.join(self.options['proj_dir'], sub)
                if os.path.exists(tgt_path):
                    sys.stderr.write('ERROR: %s already exists in %s and '
                        'cannot be overwritten by djangorecipebook\'s '
                        'template engine.\n' % (sub, self.options['proj_dir']))
                else:
                    if os.path.isdir(src_path):
                        # copy the subdirectory tree
                        shutil.copytree(src_path, tgt_path)
                        templating.process_tree(tgt_path, context)
                    else:
                        # copy the file and run templating engine
                        shutil.copy(src_path, tgt_path)
                        templating.process(tgt_path, context)
                    # mark the path as created so that it can be removed in
                    # case of a templating error
                    self.options.created(tgt_path)

        else:
            # no template name was provided, use default management command
            # 'startproject' from the django egg related to this buildout

            temp_dir = tempfile.mkdtemp('djangorecipebook')

            # so that django does not complain about missing settings
            from django.conf import settings
            settings.configure()

            # run management command
            from django.core.management import execute_from_command_line
            execute_from_command_line(['django-admin.py', 'startproject',
                                       self.name, temp_dir])

            # copy the generated files (except manage.py) in the project
            # directory
            for f in os.listdir(os.path.join(temp_dir, self.name)):
                shutil.copy(os.path.join(temp_dir, self.name, f),
                            self.options['proj_dir'])

            # erase temporary directory (manage.py is not copied)
            shutil.rmtree(temp_dir)

    def update(self):
        pass
