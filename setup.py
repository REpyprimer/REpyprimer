from __future__ import print_function
try:
    from setuptools import setup
except:
    from distutils.core import setup
import os
import sys
from warnings import warn

setup(name = 'REpyprimer',
      version = '0.1',
      author = 'Jaegun Jung',
      author_email = 'jjung@ramboll.com',
      maintainer = 'Jaegun Jung',
      maintainer_email = 'jjung@ramboll.com',
      description = 'a collection of python post- and pre-processor',
      long_description = """currently REpyprimer has rcombine.py""",
      scripts = ['scripts/rcombine.py'],
      install_requires = ['PseudoNetCDF'],
      url = 'https://github.com/REpyprimer/REpyprimer',
      classifiers = ['Programming Language :: Python :: 2.7',
                     'Operating System :: Linux',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Scientific/Engineering :: Atmospheric Science',
                    ]
      )
