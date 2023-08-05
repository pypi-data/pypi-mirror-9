# -*- coding: utf-8 -*-

import os
from setuptools import find_packages
from setuptools import setup as setup
import distutils

#############
import importStar as package
#############

#remove the old build if existent
buildpath = os.path.join(os.path.abspath(os.path.dirname(__file__)),'build')
if os.path.exists(buildpath):
    distutils.dir_util.remove_tree(buildpath)


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    p = os.path.join(*paths)
    if os.path.exists(p):
        with open(p, 'r') as f:
            return f.read()
    return ''


setup(
    name            = package.__name__,
    version         = package.__version__,
    author            = package.__author__,
    author_email    = package.__email__,
    url                = package.__url__,
    license            = package.__license__,
    install_requires= package.__depencies__,
    classifiers        = package.__classifiers__,
    description        = package.__description__,
    packages        = find_packages(exclude=['tests*']),
    include_package_data=True,
    scripts            = [os.path.join('importStar','importstar.py')],
    long_description=(
        read('README.rst') + '\n\n' +
        read('CHANGES.rst') + '\n\n' +
        read('AUTHORS.rst')),
    )
    
 
