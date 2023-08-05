#!/usr/bin/env python

"""
Setup script.

Created on Oct 10, 2011

@author: tmetsch
"""

from distutils.core import setup
from distutils.extension import Extension
try:
    from Cython.Distutils import build_ext

    BUILD_EXTENSION = {'build_ext': build_ext}
    EXT_MODULES = [Extension("dtrace", ["dtrace_consumer/dtrace_h.pxd",
                                        "dtrace_consumer/consumer.pyx"],
                             libraries=["dtrace"])]

except ImportError:
    BUILD_EXTENSION = {}
    EXT_MODULES = None
    print('WARNING: Cython seems not to be present. Currently you will only'
          ' be able to use the ctypes wrapper. Or you can install cython and'
          ' try again.')


setup(name='python-dtrace',
      version='0.0.8',
      description='DTrace consumer for Python based on libdtrace. Use Python'
                  + ' as DTrace Consumer and Provider! See the homepage for'
                  + ' more information.',
      license='MIT',
      keywords='DTrace',
      url='http://tmetsch.github.com/python-dtrace/',
      packages=['dtrace_ctypes'],
      cmdclass=BUILD_EXTENSION,
      ext_modules=EXT_MODULES,
      classifiers=["Development Status :: 2 - Pre-Alpha",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python"
                   ])
