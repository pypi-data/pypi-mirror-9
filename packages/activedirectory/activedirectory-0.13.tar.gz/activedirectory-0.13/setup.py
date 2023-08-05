#!/usr/bin/env python
# Setuptools is required for the use_2to3 option below. You should install it
# from the Distribute home page, http://packages.python.org/distribute/
from __future__ import absolute_import

import inspect
import logging
import os
import sys

from setuptools import setup, Command
from setuptools.command.test import test as TestCommand

# from distutils.core import setup, Command

from activedirectory.version import __version__

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass

test_requirements = ['pep8>=0.6', 'py>=1.4.15', 'pytest', 'six', 'sphinx']  # 'nosexcover']
test_suite = "py.test"
if sys.hexversion >= 0x02060000:
    # requirements.extend(['nose-machineout'])
    test_suite = "py.test"

# handle python 3
if sys.version_info >= (3,):
    use_2to3 = True
else:
    use_2to3 = False

options = {}

# class PyTest(Command):
#    user_options = []
#    def initialize_options(self):
#        pass
#    def finalize_options(self):
#        pass
#    def run(self):
#        import sys,subprocess
#        errno = subprocess.call([sys.executable, 'tox'])
#        raise SystemExit(errno)

"""
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)
"""


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

setup(
    name='activedirectory',
    py_modules=['activedirectory.version'],
    packages=['activedirectory'],
    version=__version__,
    zip_safe=False,
    description='Easiest way to interact with ActiveDirectory / AD / LDAP Servers from Python, pure python approach.',
    long_description=open("README.rst").read(),
    author='Sorin Sbarnea',
    author_email='sorin.sbarnea@gmail.com',
    maintainer='Sorin Sbarnea',
    maintainer_email='sorin.sbarnea@gmail.com',
    license='Python',
    platforms=['any'],
    url='https://github.com/pycontribs/activedirectory',
    download_url='https://github.com/pycontribs/activedirectory/archives/master',
    bugtrack_url='https://github.com/pycontribs/activedirectory/issues',
    keywords=['activedirectory', 'ad', 'ldap', 'ldap3'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ],
    setup_requires=['six', 'tox', 'python3-ldap'],  # ,'nosexcover'],
    tests_require=test_requirements,  # autopep8 removed because it does not install on python2.5
    test_suite=test_suite,
    cmdclass={'test': Tox},
    # use_2to3 = use_2to3,
    **options
)
