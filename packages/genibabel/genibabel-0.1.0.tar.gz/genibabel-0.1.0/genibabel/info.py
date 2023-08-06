#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" This file contains defines parameters for the project.
"""

_version_major = 0
_version_minor = 1
_version_micro = 0

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
__version__ = "%s.%s.%s" % (_version_major, _version_minor, _version_micro)

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering",
               "Topic :: Utilities"]

description = "Genetic Imaging Babel (GenIBabel)"

long_description = """
GenIBabel
=========

Genetic Imaging Babel
---------------------

A package to query genotype measures.
"""

# versions for dependencies
NUMPY_MIN_VERSION = "1.3"
SCIPY_MIN_VERSION = "0.7.2"
CWBROWSER_MIN_VERSION = "0.1.0"
PLINKIO_MIN_VERSION = "0.1.1"

# Main setup parameters
NAME = "genibabel"
MAINTAINER = "Vincent Frouin"
MAINTAINER_EMAIL = "vincent.frouin@cea.fr"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "https://bioproj.extra.cea.fr/redmine/projects/genibabel/"
DOWNLOAD_URL = ""
LICENSE = "CeCILL-B"
CLASSIFIERS = CLASSIFIERS
AUTHOR = "GenIBabel developers"
AUTHOR_EMAIL = "vincent.frouin@cea.fr"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PROVIDES = ["genibabel"]
REQUIRES = ["numpy>={0}".format(NUMPY_MIN_VERSION),
            "scipy>={0}".format(SCIPY_MIN_VERSION),
            "python-plinkio>={0}".format(PLINKIO_MIN_VERSION),
            "cwbrowser>={0}".format(CWBROWSER_MIN_VERSION)]
EXTRA_REQUIRES = {"doc": ["sphinx>=1.0"]}
