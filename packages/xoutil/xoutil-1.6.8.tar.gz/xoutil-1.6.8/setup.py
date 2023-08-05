#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os, sys
from setuptools import setup, find_packages

# Import the version from the release module
project_name = 'xoutil'
_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_current_dir, project_name))
from release import VERSION as version
from release import RELEASE_TAG

if RELEASE_TAG != '':
    dev_classifier = 'Development Status :: 4 - Beta'
else:
    dev_classifier = 'Development Status :: 5 - Production/Stable'

setup(name=project_name,
      version=version,
      description=("Collection of usefull algorithms and other very "
                   "disparate stuff"),
      long_description=open(
          os.path.join(_current_dir, 'docs', 'readme.txt')).read(),
      classifiers=[
          # Get from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          dev_classifier,
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: POSIX :: Linux',  # This is where we are
                                                 # testing. Don't promise
                                                 # anything else.
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',

      ],
      keywords='',
      author='Merchise Autrement',
      author_email='merchise.h8@gmail.com',
      url='http://github.com/merchise-autrement/',
      license='GPLv3+',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'six>=1.5.0,<2',
      ],
      extras_require={
          'extra': ['python-dateutil', ],
      },
      entry_points="""
      """,
      )
