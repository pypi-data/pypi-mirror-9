# -*- coding: utf-8 -*-
"""
This module contains the tool of wildcard.pfg.stripe
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1b6'

long_description = '%s\n%s\n%s' % (
    read('README.txt'),
    read('CHANGES.txt'),
    read('CONTRIBUTORS.txt')
)

tests_require = ['zope.testing']

setup(name='wildcard.pfg.stripe',
      version=version,
      description="Provides PFG stripe field",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone payment ecommerce stripe',
      author='Nathan Van Gheem',
      author_email='nathan@vangheem.us',
      url='https://github.com/collective/wildcard.pfg.stripe',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wildcard', 'wildcard.pfg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PloneFormGen',
          'requests',
          'collective.monkeypatcher'
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='wildcard.stripe.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
