"""
pmath
*****

Bringing the math tools of Python to the command-line
-----------------------------------------------------

Doing math on the command-line is hard. Integer math can be done with BASH, but the only utility around for floating-point math is ``bc``, and that can be confusing with its ``scale`` and ``precision``. What if you want the power of Python's math, perhaps programmatically? Enter: ``pmath``.


Examples
--------

Basic input::

  $ pmath '3 + 4'
  7
  $ echo '3+4' | pmath
  7
  $ pmath <<< 3+4
  7
  $ pmath 'x=3;x+2'
  5

You can set the output format with a ``-f`` switch::

  $ pmath -f'.4f' 'pow(2000, 1/3)'
  12.5992
  $ pmath -f'.4f' 'sin(pi/2)'
  1.0000

Enabling complex math operations is straightforward::

  $ pmath -c 'exp(1j*pi).real'
  -1.0
"""

from setuptools import setup
from os import path
import os
del os.link

setup(  name='pmath',
        version='0.2',
        
        description = ("Bringing the math tools of Python to the command-line"),
        long_description=__doc__.strip(),
        
        url = "https://pmath.lostinmy.com",
        
        author="Wendell Smith",
        author_email="wackywendell@gmail.com",
        
        license = "BSD",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Scientific/Engineering :: Mathematics",
            "Topic :: Scientific/Engineering :: Physics",
            "Intended Audience :: Science/Research",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: BSD License",
        ],
        
        keywords = "math python console command-line bash",
	packages = ['pmath'],
        

        
        # If there are data files included in your packages that need to be
        # installed, specify them here. If using Python 2.6 or less, then these
        # have to be included in MANIFEST.in as well.
        #package_data={
        #   'sample': ['package_data.dat'],
        #},
        # Although 'package_data' is the preferred approach, in some case you may
        # need to place data files outside of your packages.
        # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
        # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
        #data_files=[('my_data', ['data/data_file'])],
        # To provide executable scripts, use entry points in preference to the
        # "scripts" keyword. Entry points provide cross-platform support and allow
        # pip to create the appropriate form of executable for the target platform.

        entry_points={
            'console_scripts': [
               'pmath=pmath:main',
            ],
        }
        
)
