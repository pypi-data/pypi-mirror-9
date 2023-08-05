"""Osmosis version/release information"""

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 1
_version_micro = ''  # use '' for first of series, number for 1 and above
                     #_version_extra = 'dev'
_version_extra = ''  # Uncomment this for full releases

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: BSD License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]

description = "Read and write pdb files"

long_description = """

The PDB file format: path data-bases for tractography
-----------------------------------------------------
Based on previous work by Sherbondy, Dougherty, Wandell, and others.

Copyright (c) 2015-, Ariel Rokem.

VISTA lab, Stanford University.

All rights reserved.

"""

NAME = "pdb_files"
MAINTAINER = "Ariel Rokem"
MAINTAINER_EMAIL = "arokem@gmail.com"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "http://github.com/vistalab/pdb_files"
DOWNLOAD_URL = "https://github.com/vistalab/pdb_files/archive/master.zip"
LICENSE = "MIT"
AUTHOR = "Ariel Rokem"
AUTHOR_EMAIL = "arokem@gmail.com"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PACKAGES = ['pdb_files']
BIN = 'bin/'            
PACKAGE_DATA = {'pdb_files': ['*.py']}
PACKAGE_DIR = {'pdb_files': '.'}
REQUIRES = ["numpy", "nibabel"]
