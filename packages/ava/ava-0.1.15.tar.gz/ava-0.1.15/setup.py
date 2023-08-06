# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from ava import __version__

setup(
    name="ava",
    version=__version__,
    description="EAvatar Ava - A versatile agent.",
    # package_dir={'': ''},
    packages=find_packages(exclude=['tests']),
    include_package_data=True,

    install_requires=['backports.ssl-match-hostname',
                      'base58',
                      'bottle',
                      'click',
                      'gevent',
                      'libnacl',
                      'lmdb',
                      'msgpack-python',
                      'PyDispatcher',
                      'PyYAML',
                      'pyscrypt',
                      'requests',
                      'six',
                      'ujson',
                      'ws4py',
                      'wsaccel'],

    test_suite='nose.collector',
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'ava = ava.launcher:main',
        ],
    },

    author="Sam Kuo",
    author_email="sam@eavatar.com",
    url="http://www.eavatar.com",

)