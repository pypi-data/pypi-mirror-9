"""
Recipe generating a test script
"""

from .manage import AppsRecipe


class Recipe(AppsRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)

        options['nose'] = '1' if 'nose' in options else ''
        options.setdefault('workingdir', '')

    def _packages(self):
        pkgs = ['djangorecipebook']
        if self.options['nose']:
            pkgs.append('djangorecipebook[nose]')
        return pkgs


    def _initialization(self):
        init = super(Recipe, self)._initialization()

        if self.options['workingdir']:
            init = "os.chdir('%s')\nsys.path.append(os.getcwd())" % \
                   self.options['workingdir']

        if init and not 'import os' in init:
            init = 'import os\n' + init

        return init
