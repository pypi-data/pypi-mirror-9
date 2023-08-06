# -*- coding: utf-8 -*-
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires = [
    "TurboGears2 >= 2.2.0",
    "tgext.pluggable >= 0.0.7",
    "tgext.datahelpers >= 0.0.8"
]

testpkgs=['WebTest >= 1.2.3',
          'nose',
          'coverage',
          'sqlalchemy',
          'zope.sqlalchemy',
          'repoze.who',
          "tw2.forms",
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='tgapp-calendarevents',
    version='0.1.5',
    description='TurboGears2 pluggable application for events and calendars',
    long_description=README,
    author='Alessandro Molina',
    author_email='alessandro.molina@axant.it',
    #url='',
    keywords='turbogears2.application',
    setup_requires=[],
    paster_plugins=[],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    package_data={'tgapp.calendarevents': ['i18n/*/LC_MESSAGES/*.mo',
                                           'templates/*/*',
                                           'public/*/*']},
    entry_points="""
    """,
    dependency_links=[],
    zip_safe=False
)
