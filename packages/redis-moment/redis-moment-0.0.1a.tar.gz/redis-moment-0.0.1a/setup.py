#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join, dirname
from setuptools import setup, find_packages

from moment import __version__


with open(join(dirname(__file__), 'README.md')) as fp:
    long_description = fp.read()


setup(
    name='redis-moment',
    version=__version__,
    author='Max Kamenkov',
    author_email='mkamenkov@gmail.com',
    description='A Powerful Analytics Python Library for Redis',
    long_description=long_description,
    url='https://github.com/caxap/redis-moment',
    packages=find_packages(),
    install_requires=['redis'],
    zip_safe=False,
    include_package_data=True,
    test_suite='moment.tests',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Object Brokering',
    ]
)
