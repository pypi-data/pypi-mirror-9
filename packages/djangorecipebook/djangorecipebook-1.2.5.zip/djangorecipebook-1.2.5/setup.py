"""
djangorecipebook
Buildout recipes for django development
(c) 2014 Thomas Khyn
MIT license (see LICENSE.txt)
"""

from setuptools import setup, find_packages
import os


# imports __version__ variable
exec(open('djangorecipebook/version.py').read())
dev_status = __version_info__[3]

if dev_status == 'alpha' and not __version_info__[4]:
    dev_status = 'pre'

DEV_STATUS = {'pre': '2 - Pre-Alpha',
              'alpha': '3 - Alpha',
              'beta': '4 - Beta',
              'rc': '4 - Beta',
              'final': '5 - Production/Stable'}

install_requires = [
    'zc.buildout',
    'zc.recipe.egg',
    'django>=1.4',
]

try:
    import importlib
except ImportError:
    install_requires.append('importlib')

# setup function parameters
name = 'djangorecipebook'
setup(
    name=name,
    version=__version__,
    description='Buildout recipes for django development',
    long_description=open('README.rst').read(),
    author='Thomas Khyn',
    author_email='thomas@ksytek.com',
    url='https://bitbucket.org/tkhyn/djangorecipebook/',
    keywords=['django', 'buildout', 'recipe'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: %s' % DEV_STATUS[dev_status],
        'Intended Audience :: Developers',
        'Framework :: Buildout :: Recipe',
        'Framework :: Django',
        'Topic :: Software Development :: Build Tools',
    ],
    packages=find_packages(exclude=('tests',)),
    entry_points={'zc.buildout':
        ['%(recipe)s = %(name)s.recipes.%(recipe)s:Recipe' %
            {'recipe': recipe, 'name': name} for recipe
            in ('manage', 'wsgi', 'fcgi', 'test', 'migrate', 'makemigrations',
                'create')]
        + ['default = %s.recipes.manage:Recipe' % name]
    },
    install_requires=install_requires,
    extras_require={
        'nose': ('django_nose',),
        'south': ('south',),
    },
    zip_safe=False,
)
