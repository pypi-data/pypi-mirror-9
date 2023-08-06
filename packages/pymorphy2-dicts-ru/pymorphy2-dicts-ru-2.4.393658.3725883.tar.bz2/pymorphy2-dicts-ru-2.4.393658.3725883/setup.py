#!/usr/bin/env python
from setuptools import setup

setup(
    name = 'pymorphy2-dicts-ru',
    version = '2.4.393658.3725883',
    author = 'Mikhail Korobov',
    author_email = 'kmike84@gmail.com',
    url = 'https://github.com/kmike/pymorphy2-dicts/',

    description = 'Russian dictionaries for pymorphy2',
    long_description = open('README.rst').read(),

    license = 'MIT license',
    packages = ['pymorphy2_dicts_ru'],
    package_data = {'pymorphy2_dicts_ru': ['data/*']},
    zip_safe = False,
    entry_points = {'pymorphy2_dicts': "ru = pymorphy2_dicts_ru"},

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Linguistic',
    ],
)
