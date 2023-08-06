# -*- coding: utf-8 -*-
"""
This module contains the tool of birdhousebuilder.recipe.docker
"""
from setuptools import find_packages
from setuptools import setup

version = '0.2.1'
description = 'A Buildout recipe to generate a Dockerfile for Birdhouse applications.'
long_description = (
    open('README.rst').read() + '\n' +
    open('AUTHORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

entry_point = 'birdhousebuilder.recipe.docker'
entry_points = {"zc.buildout": [
                            "default = %s:Recipe" % entry_point,
                          ],
                "zc.buildout.uninstall": [
                            "default = %s:uninstall" % entry_point,
                          ],
                       }

tests_require = ['zope.testing', 'zc.buildout', 'manuel']

setup(name='birdhousebuilder.recipe.docker',
      version=version,
      description=description,
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Buildout',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='buildout recipe birdhouse',
      author='Birdhouse',
      url='https://github.com/bird-house/birdhousebuilder.recipe.docker',
      license='Apache License v2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['birdhousebuilder', 'birdhousebuilder.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        'Mako',
                        'birdhousebuilder.recipe.conda',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='birdhousebuilder.recipe.docker.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
