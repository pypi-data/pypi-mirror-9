#!/usr/bin/env python
from __future__ import print_function
import os
from distutils.core import setup, Command
from distutils.dir_util import remove_tree

from setuptools import setup, find_packages
from distutils.util import convert_path
from distutils.command.install import INSTALL_SCHEMES
import os, glob, platform

binwalk = "binwalk"

# The data files to install along with the module
install_data_files = []
for data_dir in ["magic", "config", "plugins", "modules", "core"]:
        install_data_files.append(os.path.join(binwalk, data_dir, '*'))

# Install the module, script, and support files
setup(name = binwalk,
      version = "2.1.0",
      description = "Firmware analysis tool",
      author = "Craig Heffner",
      url = "https://github.com/devttys0/%s" % binwalk,

      requires = [],
      packages = [binwalk],
      package_data = {binwalk : install_data_files},
      scripts = [os.path.join("scripts", binwalk)],
)

