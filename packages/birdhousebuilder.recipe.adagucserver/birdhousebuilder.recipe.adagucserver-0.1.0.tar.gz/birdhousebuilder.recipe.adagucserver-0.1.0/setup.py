# -*- coding: utf-8 -*-
"""
This module contains the tool of birdhousebuilder.recipe.adagucserver
"""
from setuptools import find_packages
from setuptools import setup

version = '0.1.0'
description = 'A Buildout recipe to install and configure Adaguc Web Mapping Service with Anaconda.'
long_description = (
    open('README.rst').read() + '\n' +
    open('AUTHORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

entry_point = 'birdhousebuilder.recipe.adagucserver'
entry_points = {"zc.buildout": [
                            "default = %s:Recipe" % entry_point,
                          ],
                "zc.buildout.uninstall": [
                            "default = %s:uninstall" % entry_point,
                          ],
                       }

tests_require = ['zope.testing', 'zc.buildout', 'manuel']

setup(name='birdhousebuilder.recipe.adagucserver',
      version=version,
      description=description,
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Buildout',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: BSD License',
      ],
      keywords='buildout recipe pywps wms birdhouse conda anaconda',
      author='Birdhouse',
      url='https://github.com/bird-house/birdhousebuilder.recipe.adagucserver',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['birdhousebuilder', 'birdhousebuilder.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
            'Mako',
            'birdhousebuilder.recipe.conda',
            'birdhousebuilder.recipe.supervisor',
            'birdhousebuilder.recipe.nginx',
            'makina.recipe.postgres',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='birdhousebuilder.recipe.adagucserver.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
