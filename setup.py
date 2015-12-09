#!/usr/bin/env python

import os

from setuptools import find_packages
from distutils.core import setup

execfile("notouch/version.py")

with open("requirements.txt") as requirements:
    required = requirements.read().splitlines()

package_data = {}

def get_package_data(package, base_dir):
    for dirpath, dirnames, filenames in os.walk(base_dir):
        dirpath = dirpath[len(package)+1:]  # Strip package dir
        for filename in filenames:
            package_data.setdefault(package, []).append(os.path.join(dirpath, filename))
        for dirname in dirnames:
            get_package_data(package, dirname)

kwargs = {
    "name": "notouch",
    "version": str(__version__),
    "packages": find_packages(exclude=['tests']),
    "package_data": package_data,
    "description": "Notouch Physical Machine Installer Automation Service",
    "author": "Matthew B Cote",
    "maintainer": "Matthew B Cote",
    "author_email": "mcot@dropbox.com",
    "maintainer_email": "mcot@dropbox.com",
    "license": "Apache",
    "install_requires": required,
    "url": "https://github.com/dropbox/notouch",
    "download_url": "https://github.com/dropbox/notouch/archive/master.tar.gz",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    "entry_points": """
       [console_scripts]
       notouch-server=notouch.server:main
    """,
}

setup(**kwargs)
