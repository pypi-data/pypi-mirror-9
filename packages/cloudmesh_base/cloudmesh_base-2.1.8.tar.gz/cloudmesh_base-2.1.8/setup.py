#!/usr/bin/env python

version = "2.1.8"

#from distutils.core import setup

from setuptools import setup, find_packages
from setuptools.command.install import install
import glob
import os
from cloudmesh_base.util import banner

banner("Installing Cloudmesh Base")

home = os.path.expanduser("~")

#
# MANAGE VERSION NUMBER
#

#
# read
#


with open("cloudmesh_base/__init__.py", "r") as f:
    content = f.read()

if content != 'version = "{0}"'.format(version):
    banner("Updating version to {0}".format(version))
    with open("cloudmesh_base/__init__.py", "w") as text_file:
        text_file.write('version="%s"' % version)

banner("Install Cloudmesh Base Requirements")
os.system("pip install -r requirements.txt")

        
'''
class UploadToPypi(install):
    """Upload the package to pypi."""
    def run(self):
        os.system("Make clean Install")
        os.system("python setup.py install")                
        banner("Build Distribution")
        os.system("python setup.py sdist --format=bztar,zip upload")        

class RegisterWithPypi(install):
    """Upload the package to pypi."""
    def run(self):
        banner("Register with Pypi")
        os.system("python setup.py register")        

        
class InstallBase(install):
    """Install the package."""
    def run(self):
        banner("Install Cloudmesh Base")
        install.run(self)

class InstallRequirements(install):
    """Install the requirements."""
    def run(self):
        banner("Install Cloudmesh Base Requirements")
        os.system("pip install -r requirements.txt")
        
class InstallAll(install):
    """Install requirements and the package."""
    def run(self):
        banner("Install Cloudmesh Base Requirements")
        os.system("pip install -r requirements.txt")
        banner("Install Cloudmesh Base")        
        install.run(self)
'''
                
setup(
    name='cloudmesh_base',
    version=version,
    description='A set of simple base functions and classes useful for cloudmesh and other programs',
    # description-file =
    #    README.rst
    author='The Cloudmesh Team',
    author_email='laszewski@gmail.com',
    url='http://github.org/cloudmesh/base',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Boot',
        'Topic :: System :: Systems Administration',
        'Framework :: Flask',
        'Environment :: OpenStack',
    ],
    packages=find_packages(),
)

