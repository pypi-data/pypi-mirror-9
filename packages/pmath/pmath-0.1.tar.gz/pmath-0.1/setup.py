"""
pmath
*****

`Code available`_ on Github.

.. _Code available: git@gist.github.com:/919042f19ab6932447df.git

Bringing the math tools of Python to the command-line
------------------------------------------

"""

from setuptools import setup
from os import path
import os
del os.link

setup(  name='pmath',
        version='0.1',
        
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
