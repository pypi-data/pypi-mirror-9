#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys


# This hack is from http://stackoverflow.com/a/7071358/1231454;
# the version is kept in a seperate file and gets parsed - this
# way, setup.py doesn't have to import the package.

VERSIONFILE = 'libfaketime/_version.py'

version_line = open(VERSIONFILE).read()
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(version_re, version_line, re.M)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '%s'" % VERSIONFILE)


_vendor_path = 'libfaketime/vendor/libfaketime'
if sys.platform == "linux" or sys.platform == "linux2":
    libname = 'libfaketime.so.1'
elif sys.platform == "darwin":
    libname = 'libfaketime.1.dylib'
else:
    raise RuntimeError("libfaketime does not support platform %s" % sys.platform)

faketime_lib = os.path.join(_vendor_path, 'src', libname)


class CustomInstall(install):
    def run(self):
        self.my_outputs = []
        subprocess.check_call(['make', '-C', _vendor_path])

        dest = os.path.join(self.install_purelib, os.path.dirname(faketime_lib))
        try:
            os.makedirs(dest)
        except OSError as e:
            if e.errno != 17:
                raise
        print faketime_lib, '->', dest
        self.copy_file(faketime_lib, dest)
        self.my_outputs.append(os.path.join(dest, libname))

        install.run(self)

    def get_outputs(self):
        outputs = install.get_outputs(self)
        outputs.extend(self.my_outputs)
        return outputs

setup(
    name='libfaketime',
    version=version,
    author='Simon Weber',
    author_email='simon@simonmweber.com',
    url='http://pypi.python.org/pypi/libfaketime/',
    packages=find_packages(),
    scripts=[],
    license='GPLv2',
    description='A fast alternative to freezegun that wraps libfaketime.',
    long_description=open('README.rst').read(),
    install_requires=[
        'contextdecorator',
        'python-dateutil >= 1.3, != 2.0',         # 2.0 is python3-only
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    zip_safe=False,
    cmdclass={'install': CustomInstall},
)
