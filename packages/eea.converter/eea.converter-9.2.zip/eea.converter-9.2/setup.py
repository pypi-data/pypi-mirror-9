""" Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

NAME = 'eea.converter'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description=("SVG, PNG, PDF converters using external "
                   "tools as ImageMagick"),
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
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
      keywords='eea converter imagemagick pdftk utility',
      author='Alin Voinea, European Environment Agency',
      author_email="webadmin@eea.europa.eu",
      maintainer='Alin Voinea (Eau de Web)',
      maintainer_email='alin@eaudeweb.ro',
      download_url="http://pypi.python.org/pypi/eea.converter",
      url='http://eea.github.com/docs/eea.converter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'kv',
          'Pillow',
          'Products.statusmessages'
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
