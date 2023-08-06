#!/usr/bin/env python

#
# This file is part of TensorToolbox.
#
# TensorToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TensorToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with TensorToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014-2015 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

import os.path
import sys, getopt, re
from setuptools import setup, find_packages 

setup_deps = ['Cython']
deps = ['Sphinx','prettytable', 'UQToolbox >= 0.1', 'SpectralToolbox >= 0.1','scipy','numpy','h5py']
if "--without-mpi4py" in sys.argv:
    idx = sys.argv.index('--without-mpi4py')
    del sys.argv[idx]
else:
    deps.append( 'mpi_map' )
    
local_path = os.path.split(os.path.realpath(__file__))[0]
version_file = os.path.join(local_path, 'TensorToolbox/_version.py')
version_strline = open(version_file).read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, version_strline, re.M)
if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (version_file,))

setup(name = "TensorToolbox",
      version = version,
      packages=find_packages(),
      include_package_data=True,
      scripts=["scripts/TensorToolboxUpV030"],
      url="http://www2.compute.dtu.dk/~dabi/",
      author = "Daniele Bigoni",
      author_email = "dabi@dtu.dk",
      license="COPYING.LESSER",
      description="Tools for the decomposition of tensors",
      long_description=open("README.txt").read(),
      zip_safe = False,         # I need this for MPI purposes
      setup_requires=setup_deps,
      install_requires=deps
      )
