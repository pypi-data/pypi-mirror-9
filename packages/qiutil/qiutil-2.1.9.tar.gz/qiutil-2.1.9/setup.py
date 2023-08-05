import os
import re
import subprocess
import glob
from setuptools import (setup, find_packages)

def version(package):
    """
    Return package version as listed in the `__init.py__` `__version__`
    variable.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def requires():
    """
    @return: the ``requirements.txt`` package specifications
    """
    with open('requirements.txt') as f:
        return f.read().splitlines()
        

def readme():
    with open("README.rst") as f:
        return f.read()

# Note: bdist binary distribution is not supported because of the
# following setuptools bug:
#
# * setuptools bdist cannot include selective top-level files and
#   directories. Contrary to
#   http://stackoverflow.com/questions/7522250/how-to-include-package-data-with-setuptools-distribute,
#   there is no known combination of package_data, include_package_data
#   and MANIFEST.in that includes selective top-level files and directories
#   in both the source and binary distributions.
#
#   The work-around is to only build the source distribution. This is done
#   as follows:
#
#   1. Set MANIFEST.in to the following:
#
#          include *.rst *.txt
#          recursive-exclude test *
#
#      recursive-exclude excludes the test files. Note that this entry is
#      only strictly necessary for some projects, e.g. qidicom, but not
#      others, e.g. qiutil. The reason for this difference is unknown, but
#      is probably due to another obscure setuptools bug. At any rate, it
#      doesn't hurt to include it in all projects. It is advisable to
#      exclude the test directory because only python files are included,
#      and the python test cases often require test fixtures.
#
#   2. Place all directories necessary for package use, e.g. conf,
#      in the package source parent directory.
#
#   3. Add the package_data option to the setup call, e.g.:
#
#          package_data = dict(qiutil=['conf/*']),
#  
#   4. Build the source distribution:
#
#          python setup.py sdist
#
#   5. Upload the distribution to PyPI:
#
#          twine upload dist/*
#
# TODO - revisit this when the python 3.x package module is released.
#
setup(
    name = 'qiutil',
    version = version('qiutil'),
    author = 'OHSU Knight Cancer Institute',
    author_email = 'loneyf@ohsu.edu',
    platforms = 'Any',
    license = 'MIT',
    keywords = 'Imaging QIN',
    packages = find_packages(exclude=['test**']),
    package_data = dict(qiutil=['conf/*']),
    url = 'http://qiutil.readthedocs.org/en/latest/',
    description = 'Quantitative Imaging helper utilities',
    long_description = readme(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    install_requires = requires()
)
