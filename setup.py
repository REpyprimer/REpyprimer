from __future__ import print_function
try:
    from setuptools import setup
except:
    from distutils.core import setup
import os
import sys
from warnings import warn
def find_packages():
    import os
    packages = []
    walker = os.walk('src')
    prefix = os.path.join(os.path.curdir,'src')
    for thisdir, itsdirs, itsfiles in walker:
        if '__init__.py' in itsfiles:
            packages.append(thisdir[len(prefix)-1:])
    
    return packages
            
def find_data():
    import os
    import re
    data_pattern = re.compile(r'.*(.|_)(yaml|nc|net|irr|phy|ptb|sum|voc|txt|xls|graffle)$')
    data = []
    prefix = os.path.join(os.path.curdir,'src', 'REpyprimer')
    walker = os.walk('src')
    for thisdir, itsdirs, itsfiles in walker:
        if thisdir != os.path.join('src','REpyprimer.egg-info'):
            data.extend([os.path.join(thisdir[len(prefix)-1:],f) for f in itsfiles if data_pattern.match(f) is not None])
    
    return data

packages = find_packages()
data = find_data()

setup(name = 'REpyprimer',
      version = '0.1',
      author = 'Jaegun Jung',
      author_email = 'jjung@ramboll.com',
      maintainer = 'Jaegun Jung',
      maintainer_email = 'jjung@ramboll.com',
      description = 'a collection of python post- and pre-processor',
      long_description = """currently REpyprimer has rcombine.py""",
      packages = packages,
      package_dir = {'': 'src'},
      package_data = {'REpyprimer': data},
      scripts = ['scripts/rcombine.py'],
      url = 'https://github.com/REpyprimer/REpyprimer',
      classifiers = ['Programming Language :: Python :: 2.7',
                     'Operating System :: Linux',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Scientific/Engineering :: Atmospheric Science',
                    ]
      )
