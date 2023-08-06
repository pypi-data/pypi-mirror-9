#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages

from sshmount_netrc import __version__

setup(
    name='sshmount-netrc',
    version=__version__,
    # Your name & email here
    author='Tjaart van der Walt',
    author_email='pypi@tjaart.co.za',
    # If you had sshmount_netrc.tests, you would also include that in this list
    packages=find_packages(),
    # Any executable scripts, typically in 'bin'. E.g 'bin/do-something.py'
    scripts=['sshmount_netrc/sshmount_netrc.py'],
    # REQUIRED: Your project's URL
    url='https://github.com/tjaartvdwalt/sshmount-netrc',
    # Put your license here. See LICENSE.txt for more information
    license='MIT',
    # Put a nice one-liner description here
    description='ssh mount using passwords saved in .netrc',
    long_description="Mount ssh filesystems using the passwords saved in your .netrc file",
    # Any requirements here, e.g. "Django >= 1.1.1"
    install_requires=[
    ],
    platforms=['Linux'],
)
