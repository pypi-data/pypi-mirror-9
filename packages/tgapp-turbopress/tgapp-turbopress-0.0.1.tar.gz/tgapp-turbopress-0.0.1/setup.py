# -*- coding: utf-8 -*-
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires=[
    "TurboGears2 >= 2.3.0",
    "formencode",
    "webhelpers",
    "tw2.forms",
    "tw2.jquery",
    "tgext.pluggable",
    "tgext.datahelpers",
    "tgext.ajaxforms",
    "tgext.crud",
    "sprox >= 0.9.1",
    "genshi"
]

testpkgs=['WebTest >= 1.2.3',
          'nose',
          'coverage',
          'ming',
          'sqlalchemy',
          'zope.sqlalchemy',
          'repoze.who'
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='tgapp-turbopress',
    version='0.0.1',
    description='Pluggable Blog for TurboGears2 supporting SQLAlchemy and MongoDB',
    long_description=README,
    author='AXANT',
    author_email='tech@axant.it',
    url='http://bitbucket.org/axant/tgapp-turbopress',
    keywords='turbogears2.application',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=testpkgs,
    extras_require={
       # Used by Drone.io
       'testing':testpkgs,
    },
    include_package_data=True,
    package_data={'tgapp.turbopress': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    entry_points="""
    """,
    zip_safe=False
)
