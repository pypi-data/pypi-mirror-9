"""
Recipe generating a script for database migration
"""

from .manage import AppsRecipe


class Recipe(AppsRecipe):

    def __init__(self, buildout, name, options):
        # a settings module is needed, one cannot use minimal settings
        # to migrate a database !
        options.setdefault('settings', 'settings')
        super(Recipe, self).__init__(buildout, name, options)

    def _packages(self):
        pkgs = ['djangorecipebook']
        if self.django_version < (1, 7):
            pkgs.append('djangorecipebook[south]')
        return pkgs
