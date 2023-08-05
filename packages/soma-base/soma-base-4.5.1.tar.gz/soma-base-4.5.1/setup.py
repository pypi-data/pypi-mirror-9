#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

from ez_setup import use_setuptools
use_setuptools()

import os
from setuptools import setup, find_packages
from datetime import datetime

release_info = {}
execfile(os.path.join("soma", "info.py"), release_info)

setup(
    name=release_info["NAME"],
    description=release_info["DESCRIPTION"],
    long_description=release_info["LONG_DESCRIPTION"],
    license=release_info["LICENSE"],
    classifiers=release_info["CLASSIFIERS"],
    author=release_info["AUTHOR"],
    author_email=release_info["AUTHOR_EMAIL"],
    version=release_info["VERSION"],
    packages=find_packages(),
    platforms=release_info["PLATFORMS"],
    #scripts=["../../bin/bv_minf_2_XML", ]
)
