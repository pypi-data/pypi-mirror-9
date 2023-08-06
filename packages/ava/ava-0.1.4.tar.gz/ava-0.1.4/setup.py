# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="ava",
    version="0.1.4",
    description="EAvatar Ava - A versatile agent.",
    # package_dir={'': ''},
    packages=find_packages(exclude=['tests']),
    include_package_data=True,

    # install_requires = ['setuptools'],
    test_suite='nose.collector',
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'ava = avacli:main',
        ],
    },

    author="Sam Kuo",
    author_email="sam@eavatar.com",
    url="http://www.eavatar.com",

)