#!/usr/bin/env python

#
# This file is part of phantom_scheduler.
#
# phantom_scheduler is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# phantom_scheduler is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with phantom_scheduler.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

import os.path
import sys, getopt, re
from setuptools import setup, find_packages 

deps = []
    
local_path = os.path.split(os.path.realpath(__file__))[0]
version_file = os.path.join(local_path, 'phantom_scheduler/_version.py')
version_strline = open(version_file).read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, version_strline, re.M)
if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (version_file,))

setup(name = "phantom_scheduler",
      version = version,
      packages=find_packages(),
      include_package_data=True,
      scripts=["scripts/phantom",
               "scripts/psrunner",
               "scripts/psqsub",
               "scripts/psqrsh",
               "scripts/ps-job-example",
               "scripts/ps-sched-localhost-nonblocking-example",
               "scripts/ps-sched-localhost-blocking-example",
               "scripts/ps-sched-cluster-nonblocking-example",
               "scripts/ps-sched-cluster-blocking-example"],
      url="http://www2.compute.dtu.dk/~dabi/",
      author = "Daniele Bigoni",
      author_email = "dabi@dtu.dk",
      license="COPYING.LESSER",
      description="Artificial scheduler for clusters",
      long_description=open("README.txt").read(),
      zip_safe = False,
      install_requires=deps
      )
