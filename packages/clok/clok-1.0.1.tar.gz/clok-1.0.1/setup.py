#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages
import clok

setup(
    name='clok',
    version=clok.__version__,
    install_requires=['docopt', 'bottle', 'tinydb', 'pyradio', 'requests', 'waitress'],
    packages=find_packages(),
    author='fspot',
    author_email='fred@fspot.org',
    description='Listen to radio and set up alarms from your computer, control it from a web ui.',
    long_description=open('README.md').read(),
    include_package_data=True,
    zip_safe=False,
    url='http://github.com/fspot/clok',
    entry_points = {
        'console_scripts': [
            'clok = clok.server:main',
        ],
    },
    license='BSD',
)
