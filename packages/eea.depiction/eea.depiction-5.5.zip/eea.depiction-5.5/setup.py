""" Installer
"""
from setuptools import setup, find_packages
import os

NAME = 'eea.depiction'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="EEA Depiction (formerly valentine.imagescales)",
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
        ],
      keywords='eea depiction image scales thumbnails',
      author='European Environment Agency',
      author_email="webadmin@eea.europa.eu",
      url='http://eea.github.com/docs/eea.depiction',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Pillow',
        ],
      extras_require={
          'full': [
              'p4a.video',
            ],
          'test': [
              'plone.app.testing'
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
