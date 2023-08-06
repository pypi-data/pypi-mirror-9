"""
Recipe generating a wsgi script
"""

from .fcgi import Recipe as FcgiRecipe


wsgi_template = """
%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %(path)s,
  ]
%(initialization)s
import %(module_name)s

application = %(module_name)s.%(attrs)s(%(arguments)s)
"""


class Recipe(FcgiRecipe):
    script_template = wsgi_template

    def __init__(self, buildout, name, options):
        options.setdefault('application', '')
        super(Recipe, self).__init__(buildout, name, options)

    def _arguments(self):
        args = super(Recipe, self)._arguments()

        if self.options['application']:
            args += ", application='%s'" % self.options['application']

        return args
