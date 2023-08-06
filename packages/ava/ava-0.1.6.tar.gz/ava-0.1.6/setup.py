# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="ava",
    version="0.1.6",
    description="EAvatar Ava - A versatile agent.",
    # package_dir={'': ''},
    packages=find_packages(exclude=['tests']),
    include_package_data=True,

    install_requires=['base58>=0.2.1',
                      'bottle>=0.12.8',
                      'click==3.3',
                      'gevent==1.0.1',
                      'libnacl==1.4.0',
                      'lmdb==0.84',
                      'pycrypto==2.6.1',
                      'PyDispatcher==2.0.5',
                      'PyYAML==3.11',
                      'pyscrypt==1.6.2'],
    test_suite='nose.collector',
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'ava = ava.main:main',
        ],
    },

    author="Sam Kuo",
    author_email="sam@eavatar.com",
    url="http://www.eavatar.com",

)