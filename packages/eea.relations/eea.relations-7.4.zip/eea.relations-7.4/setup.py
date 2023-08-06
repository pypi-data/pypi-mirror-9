""" Installer
"""
import os
from setuptools import setup, find_packages

NAME = 'eea.relations'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=("EEA Possible Relations. This package provides a flexible "
                   "way to manage relations in a Plone site. it provides a new "
                   "reference browser widget and a central management "
                   "interface for relations, their labels and requirements."),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Framework :: Plone",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Programming Language :: Zope",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "License :: OSI Approved :: Mozilla Public License 1.0 (MPL)",
        ],
      keywords=('eea relations widget reference browser referencebrowserwidget '
                'faceted facetednavigation plone zope python'),
      author='European Environment Agency',
      author_email="webadmin@eea.europa.eu",
      url='http://eea.github.com/docs/eea.relations',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pydot',
          'eea.jquery > 8.0',
          'eea.facetednavigation',
          'Products.TALESField',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
