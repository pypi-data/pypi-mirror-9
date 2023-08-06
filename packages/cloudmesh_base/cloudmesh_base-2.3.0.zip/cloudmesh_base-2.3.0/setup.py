#!/usr/bin/env python

version = "2.3.0"

requirements = [
        'future',             
        'sh',
        'docopt',
        'pyaml',
        'simplejson',
        'nose',
        'python-hostlist',
        'prettytable',
        'pytimeparse',
    ]

# from distutils.core import setup

from setuptools import setup, find_packages
from setuptools.command.install import install
import os
from cloudmesh_base.util import banner


#
# AUTOCREATE REQUIREMENTS FROM ARRAY
#
def auto_create_requirements():
    banner("Creating requirements.txt file")
    with open("requirements.txt", "r") as f:
        file_content = f.read()
        
    setup_requirements = '\n'.join(requirements)
    
    if setup_requirements != file_content:
        with open("requirements.txt", "w") as text_file:
            text_file.write(setup_requirements)


banner("Installing Cloudmesh Base")

home = os.path.expanduser("~")

#
# MANAGE VERSION NUMBER
#


def auto_create_version():
    with open("cloudmesh_base/__init__.py", "r") as f:
        content = f.read()
    
    if content != 'version = "{0}"'.format(version):
        banner("Updating version to {0}".format(version))
        with open("cloudmesh_base/__init__.py", "w") as text_file:
            text_file.write('version = "%s"' % version)

auto_create_version()

# banner("Install Cloudmesh Base Requirements")
# os.system("pip install -r requirements.txt")


class CreateRequirementsFile(install):
    """Create the requiremnets file."""
    def run(self):    
        auto_create_requirements()
        
        
class UploadToPypi(install):
    """Upload the package to pypi."""
    def run(self):
        auto_create_version()
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
        },
)

