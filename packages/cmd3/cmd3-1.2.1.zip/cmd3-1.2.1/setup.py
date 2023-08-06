#!/usr/bin/env python
# -------------------------------------------------------------------------- #
# Copyright 2008-2010, Gregor von Laszewski                                  #
# Copyright 2010-2013, Indiana University                                    #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #

version = "1.2.1"

from setuptools import setup, find_packages
from setuptools.command.install import install
import os
from setuptools import setup, find_packages
from cloudmesh_base.util import banner
from cloudmesh_base.util import path_expand
from cloudmesh_base.Shell import Shell
import shutil

banner("Installing Cmd3")



with open("cmd3/__init__.py", "r") as f:
    content = f.read()

if content != 'version = "{0}"'.format(version):
    banner("Updating version to {0}".format(version))
    with open("cmd3/__init__.py", "w") as text_file:
        text_file.write('version="%s"' % version)

class SetupYaml(install):
    """Upload the package to pypi."""
    def run(self):
        banner("Setup the cmd3.yaml file")

        cmd3_yaml = path_expand("~/.cloudmesh/cmd3.yaml")
        
        if os.path.isfile(cmd3_yaml):
            print ("ERROR: the file {0} already exists".format(cmd3_yaml))
            print
            print ("If you like to reinstall it, please remove the file")
        else:
            print ("Copy file:  {0} -> {1} ".format(path_expand("etc/cmd3.yaml"), cmd3_yaml))
            Shell.mkdir("~/.cloudmesh")
            
            shutil.copy("etc/cmd3.yaml", path_expand("~/.cloudmesh/cmd3.yaml"))

class InstallBase(install):
    """Install the package."""
    def run(self):
        banner("Install Cmd3")
        install.run(self)
        
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    version=version,
    name="cmd3",
    description="cmd3 - A dynamic CMD shell with plugins",
    long_description=read('README.rst'),
    license="Apache License, Version 2.0",
    author="Gregor von Laszewski",
    author_email="laszewski@gmail.com",
    url="https://github.com/cloudmesh/cmd3",
    classifiers=[
         "Intended Audience :: Developers",
         "Intended Audience :: Education",
         "Intended Audience :: Science/Research",
         "Development Status :: 5 - Production/Stable",
         "Intended Audience :: Developers",
         "License :: OSI Approved :: Apache Software License",
         "Operating System :: MacOS :: MacOS X",
         "Operating System :: POSIX :: Linux",
         "Programming Language :: Python :: 2.7",
         "Topic :: Scientific/Engineering",
         "Topic :: System :: Clustering",
         "Topic :: System :: Distributed Computing",
         "Topic :: Software Development :: Libraries :: Python Modules",
         "Environment :: Console"
         ],
    keywords="cmd commandshell plugins",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cm = cmd3.shell:main',
        ],
    },
    cmdclass={
        'install': InstallBase,
        'yaml': SetupYaml,
        },
 )

