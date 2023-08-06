#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyHum - a Python framework for sidescan data texture classification.

PyHum is an open-source project dedicated to provide a Python framework for
processing low-cost sidescan data. It provides parsers for Humminbird file formats,
and signal processing routines which allow the manipulation of sidescan data and automated texture classification 

For more information visit http://dbuscombe-usgs.github.io/PyHum/

:install:
    python setup.py install
    sudo python setup.py install
    
:test:
    python -c "import PyHum; PyHum.test.dotest()"

:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
    
    This software is in the public domain because it contains materials that
    originally came from the United States Geological Survey, an agency of the
    United States Department of Interior. For more information, 
    see the official USGS copyright policy at
    http://www.usgs.gov/visual-id/credit_usgs.html#copyright
    Any use of trade, product, or firm names is for descriptive purposes only 
    and does not imply endorsement by the U.S. government.
    
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os, sys, glob
import inspect
try:
    import numpy as np
except:
    msg = ("No module named numpy. "
           "Please install numpy first, it is needed before installing PyHum.")
    raise ImportError(msg)

from distutils.core import setup
from distutils.extension import Extension
#from setuptools import setup, Extension

# Directory of the current file 
SETUP_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe())))

# Set this to True to enable building extensions using Cython.
# Set it to False to build extensions from the C file (that
# was previously created using Cython).
# Set it to 'auto' to build with Cython if available, otherwise
# from the C file.
USE_CYTHON = True

if USE_CYTHON:
   try:
      from Cython.Distutils import build_ext
   except:
      msg = ("No module named Cython. "
           "Please install Cython first, it is needed before installing PyHum.")
      raise ImportError(msg)

#if USE_CYTHON:
#    try:
#        from Cython.Distutils import build_ext
#    except ImportError:
#        if USE_CYTHON=='auto':
#            USE_CYTHON=False
#        else:
#            raise

# Read version from distmesh/__init__.py
with open(os.path.join('PyHum', '__init__.py')) as f:
    line = f.readline()
    while not line.startswith('__version__'):
        line = f.readline()
exec(line, globals())

ext_modules = [ ]
cmdclass = { }

if USE_CYTHON:
    ext_modules += [
        Extension("PyHum.cwt", [ "PyHum/_cwt.pyx" ],
        include_dirs=[np.get_include()]),
        Extension("PyHum.pyread", [ "PyHum/_pyread.pyx" ],
        include_dirs=[np.get_include()]),
        Extension("PyHum.ppdrc", [ "PyHum/_ppdrc.pyx" ],
        include_dirs=[np.get_include()]),    
        Extension("PyHum.replace_nans", [ "PyHum/_replace_nans.pyx" ],
        include_dirs=[np.get_include()]),
        Extension("PyHum.spec_noise", [ "PyHum/_spec_noise.pyx" ],
        include_dirs=[np.get_include()]),
        Extension("PyHum.stdev", [ "PyHum/_stdev.pyx" ],
        include_dirs=[np.get_include()]),
        Extension('_RunningStats',sources=['PyHum/RunningStats_wrap.cxx', 'PyHum/RunningStats.cpp', 'PyHum/RunningStats.h']),
    ]
    cmdclass.update({ 'build_ext': build_ext })
else:
    ext_modules += [
        Extension("PyHum.cwt", [ "PyHum/_cwt.c" ],
        include_dirs=[np.get_include()]),
        Extension("PyHum.pyread", [ "PyHum/_pyread.c" ],
        include_dirs=[np.get_include()]),
        Extension("PyHum.ppdrc", [ "PyHum/_ppdrc.c" ],
        include_dirs=[np.get_include()]),   
        Extension("PyHum.replace_nans", [ "PyHum/_replace_nans.c" ],
        include_dirs=[np.get_include()]),
        Extension("PyHum.spec_noise", [ "PyHum/_spec_noise.c" ],
        include_dirs=[np.get_include()]),
        Extension("PyHum.stdev", [ "PyHum/_stdev.c" ],
        include_dirs=[np.get_include()]),
        Extension('_RunningStats',sources=['PyHum/RunningStats_wrap.cxx', 'PyHum/RunningStats.cpp', 'PyHum/RunningStats.h']),
    ]
install_requires = [
    'numpy','scipy','Pillow','matplotlib', 'cython', 'pyproj', 'scikit-image', 'simplekml'
]
#'scikit-learn',
#long_description = open('README.md').read()

def setupPackage():
   setup(name='PyHum',
         version=__version__,
         description='Python/Cython scripts to read Humminbird DAT and associated SON files, export data, carry out rudimentary radiometric corrections to data, and classify bed texture using the algorithm detailed in Buscombe, Grams, Smith, "Automated riverbed sediment classification using low-cost sidescan sonar", forthcoming.',
         #long_description=long_description,
         classifiers=[
             'Intended Audience :: Science/Research',
             'Intended Audience :: Developers',
             'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
             'Programming Language :: Python',
             'Programming Language :: Python :: 2.7',
             'Programming Language :: Cython',
             'Topic :: Scientific/Engineering',
             'Topic :: Scientific/Engineering :: Physics',
         ],
         keywords='sidescan sonar humminbird sediment substrate classification',
         author='Daniel Buscombe',
         author_email='dbuscombe@usgs.gov',
         url='https://github.com/dbuscombe-usgs/PyHum',
         download_url ='https://github.com/dbuscombe-usgs/PyHum/archive/master.zip',
         install_requires=install_requires,
         license = "GNU GENERAL PUBLIC LICENSE v3",
         packages=['PyHum'],
         cmdclass = cmdclass,
         ext_modules=ext_modules,
         platforms='OS Independent',
         package_data={'PyHum': ['*.SON', '*.DAT',]}
   )

if __name__ == '__main__':
    # clean --all does not remove extensions automatically
    if 'clean' in sys.argv and '--all' in sys.argv:
        import shutil
        # delete complete build directory
        path = os.path.join(SETUP_DIRECTORY, 'build')
        try:
            shutil.rmtree(path)
        except:
            pass
        # delete all shared libs from lib directory
        path = os.path.join(SETUP_DIRECTORY, 'PyHum')
        for filename in glob.glob(path + os.sep + '*.pyd'):
            try:
                os.remove(filename)
            except:
                pass
        for filename in glob.glob(path + os.sep + '*.so'):
            try:
                os.remove(filename)
            except:
                pass
    setupPackage()

