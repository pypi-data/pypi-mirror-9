#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import sys
import ast


def get_version(filename):
    """Detects the current version."""
    with open(filename) as f:
        tree = ast.parse(f.read(), filename)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, = node.targets
            if isinstance(target, ast.Name) and target.id == '__version__':
                return node.value.s
    raise ValueError('__version__ not found from {0}'.format(filename))


settings = dict()

install_requires = ['six', 'xxhash', 'spooky']
if sys.version_info < (2, 7):
    install_requires.append('argparse')

test_requires = ['coverage', 'mock', 'nose']

setup(
    name='csample',
    version=get_version('csample.py'),
    description='Sampling library for Python',
    long_description=open('README.rst').read(),
    author='Alan Kang',
    author_email='alankang@boxnwhis.kr',
    url='https://github.com/box-and-whisker/csample',
    py_modules=['csample'],
    package_data={'': ['README.rst']},
    include_package_data=True,
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='tests',
    license='MIT License',
    platforms='any',
    keywords='hash filter sample log analysis streaming',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Text Processing :: Filters',
    ],
    entry_points={
        'console_scripts': [
            'csample=csample:main',
        ],
    },
)
