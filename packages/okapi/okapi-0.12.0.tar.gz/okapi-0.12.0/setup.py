# Copyright 2014 Red Beacon, Inc.  All Rights Reserved
#
# This code, and all derivative work, is the exclusive property of
# Red Beacon, Inc. and may not be used without Red Beacon, Inc.'s
# authorization.
#
# Author: Gobind Ball

import os.path

from setuptools import find_packages
from setuptools import setup

from okapi import __version__

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name='okapi',
    version=__version__,
    author='RedBeacon (Gobind Ball)',
    author_email='support@redbeacon.com',
    description=README + '\n\n' + CHANGES,
    packages=find_packages(),
    data_files=[('config',['setup.cfg'])],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
    ],
    zip_safe=False,
    install_requires = [
        'pymongo',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'okapi=okapi:mongo',
        ],
    },
)