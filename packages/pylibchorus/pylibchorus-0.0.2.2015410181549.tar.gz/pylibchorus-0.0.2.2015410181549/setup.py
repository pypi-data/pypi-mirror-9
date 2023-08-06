#!/usr/bin/env python
'''pylibchorus setup'''

import os
from setuptools import setup, find_packages

VERSION = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), 'pylibchorus', 'version.py')

exec(compile(open(VERSION).read(), VERSION, 'exec'))

def gen_build_num():
    from datetime import datetime
    now = datetime.now()
    return ''.join(str(x) for x in (now.year,
                                    now.month,
                                    now.day,
                                    now.hour,
                                    now.minute,
                                    now.second))


def read(fname):
    return "\n" + open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pylibchorus",
    version=__version__ + '.' + gen_build_num(),
    author="Kenny Ballou",
    author_email="kb@alpinenow.com",
    url="http://alpinenow.com",
    description=("Python Chorus API Library"),
    packages=find_packages(),
    test_suite="pylibchorus.tests",
    package_data={
    },
    long_description=read("README.markdown"),
    install_requires=[
        'requests',
        'setuptools',
    ],
    tests_require=[
        'unittest2',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
