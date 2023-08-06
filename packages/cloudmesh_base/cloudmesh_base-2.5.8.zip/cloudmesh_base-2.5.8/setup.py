#!/usr/bin/env python

version = "2.5.8"

# from distutils.core import setup

from setuptools import setup, find_packages
from setuptools.command.install import install
import os
from cloudmesh_base.util import banner
from cloudmesh_base.util import auto_create_version
from cloudmesh_base.util import path_expand
import shutil


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


requirements = parse_requirements('requirements.txt')

banner("Installing Cloudmesh Base")

home = os.path.expanduser("~")

#
# MANAGE VERSION NUMBER
#

auto_create_version("cloudmesh_base", version)

# banner("Install Cloudmesh Base Requirements")
# os.system("pip install -r requirements.txt")


class CreateRequirementsFile(install):
    """Create the requiremnets file."""
    def run(self):    
        auto_create_requirements()
        
        
class UploadToPypi(install):
    """Upload the package to pypi."""
    def run(self):
        auto_create_version("cloudmesh_base", version)
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
        auto_create_requirements()
        banner("Install Cloudmesh Base Requirements")
        os.system("pip install -r requirements.txt")
        

class InstallAll(install):
    """Install requirements and the package."""
    def run(self):
        banner("Install Cloudmesh Base Requirements")
        os.system("pip install -r requirements.txt")
        banner("Install Cloudmesh Base")        
        install.run(self)


class SetupYaml(install):
    """Upload the package to pypi."""

    def run(self):
        banner("Setup the cloudmesh_database.yaml file")

        database_yaml = path_expand("~/.cloudmesh/cloudmesh_database.yaml")

        if os.path.isfile(database_yaml):
            print ("WARNING: the file {0} already exists".format(database_yaml))
            print
            print ("If you like to reinstall it, please remove the file")
        else:
            print ("Copy file:  {0} -> {1} ".format(path_expand("etc/cloudmesh_database.yaml"), database_yaml))
            os.makedirs(path_expand("~/.cloudmesh"))

            shutil.copy("etc/cloudmesh_database.yaml", path_expand("~/.cloudmesh/cloudmesh_database.yaml"))

class CreateDoc(install):
    """Install requirements and the package."""

    def run(self):
        banner("Create Documentation")
        os.system("python setup.py install")
        os.system("sphinx-apidoc -o docs/source cloudmesh_database cloudmesh_base")
        os.system("cd docs; make -f Makefile html")

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
    install_requires=requirements,
    packages=find_packages(),
    cmdclass={
        'install': InstallBase,
        'requirements': InstallRequirements,
        'all': InstallAll,
        'pypi': UploadToPypi,
        'pypiregister': RegisterWithPypi, 
        'create_requirements': CreateRequirementsFile,
        'yaml': SetupYaml,
        'doc': CreateDoc,
        },
)

