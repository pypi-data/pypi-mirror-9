#!/usr/bin/env python

from distutils.core import setup

setup(name='hyperspace',
      version='0.1.0',
      packages=['hyperspace'],
      description='General-purpose REST/hypermedia client.',
      author='Ross Fenning',
      author_email='ross.fenning@gmail.com',
      url='http://rossfenning.co.uk/',
      license='GPLv3+',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      install_requires=[
          'requests',
          'rdflib',
          'rdflib-jsonld',
          'beautifulsoup4',
          'html5lib',
      ],
)
