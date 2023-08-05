#!/usr/bin/env python
"""Distribution Utilities setup program for MyProxy Client Package

NERC DataGrid Project
"""
__author__ = "P J Kershaw"
__date__ = "12/12/08"
__copyright__ = "(C) 2011 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory

Software adapted from myproxy_logon.  - For myproxy_logon see Access Grid 
Toolkit Public License (AGTPL)

This product includes software developed by and/or derived from the Access 
Grid Project (http://www.accessgrid.org) to which the U.S. Government retains 
certain rights."""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'

# Bootstrap setuptools if necessary.
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import os
THIS_DIR = os.path.dirname(__file__)

# Read succeeds for sdist creation but fails for build with pip install.  Added
# catch here for latter case.
try:
    LONG_DESCR = open(os.path.join(THIS_DIR, 'README.md')).read()
except IOError:
    LONG_DESCR = ('Python implementation of a client to the MyProxy '
        'Credential Management Server (http://grid.ncsa.uiuc.edu/myproxy/) ')

setup(
    name =            	'MyProxyClient',
    version =         	'1.4.3',
    description =     	'MyProxy Client',
    long_description = 	LONG_DESCR,
    author =          	'Philip Kershaw',
    author_email =    	'Philip.Kershaw@stfc.ac.uk',
    maintainer =        'Philip Kershaw',
    maintainer_email =  'Philip.Kershaw@stfc.ac.uk',
    url =             	'https://github.com/cedadev/MyProxyClient',
    platforms =         ['POSIX', 'Linux', 'Windows'],
    install_requires =  ['pyOpenSSL'],
    license =           __license__,
    test_suite =        'myproxy.test',
    packages =          find_packages(),
    include_package_data = True,
    package_data =      {
        '': ['README.md'],
        'myproxy.test': ['*.cfg', '*.conf', '*.crt', '*.key', 'README']
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (BSD)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe = False,
    entry_points = {
        'console_scripts': ['myproxyclient = myproxy.script:main',
                            ],
        }
)
