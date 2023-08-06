import os
import imp


def find_module_path(module):
    """
    Returns the path to a given module, without importing it or any parent
    module
    Raises ImportError if the module does not seem to exist
    """

    module_py_path = module.split('.')
    module_py_path.reverse()
    path = imp.find_module(module_py_path.pop())[1]
    while module_py_path:
        path = os.path.join(path, module_py_path.pop())

    if os.path.isfile(path + '.py'):
        return path + '.py'

    if not os.path.isfile(os.path.join(path, '__init__.py')):
        raise ImportError('Could not find module "%s"' % module)

    return path


def get_migrations_type(mig_path):
    """
    Checks if the path contains migrations and returns the type ('south' or
    'django'), and None if no migrations found
    """

    if os.path.isfile(os.path.join(mig_path, '__init__.py')):
        # there is a migration subpackage, look for the first
        # migration file
        for f in os.listdir(mig_path):
            if f.endswith('.py') and f != '__init__.py':
                # migration found, check if it is a south migration
                mig = open(os.path.join(mig_path, f))
                south_mig = 'from south.db import db' in mig.read()
                mig.close()
                return 'south' if south_mig else 'django'
        else:
            return None
