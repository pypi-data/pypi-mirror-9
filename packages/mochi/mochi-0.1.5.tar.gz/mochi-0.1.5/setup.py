#!/usr/bin/env python
from setuptools import setup, find_packages
from mochi import __author__, __version__, __license__, IS_PYTHON_34

install_requires = ['rply>=0.7.3',
                    'pyrsistent>=0.7.1',
                    'greenlet>=0.4.5',
                    'eventlet>=0.16.1']


if not IS_PYTHON_34:
    install_requires.append('pathlib>=1.0.1')


def is_windows():
    from sys import platform
    return platform.startswith('win') or platform.startswith('cygwin')

if is_windows():
    readme = ''
else:
    with open('README.rst', 'r') as f:
        readme = f.read()

setup(
    name='mochi',
    version=__version__,
    description='Dynamically typed functional programming language',
    long_description=readme,
    license=__license__,
    author=__author__,
    url='https://github.com/i2y/mochi',
    platforms=['any'],
    entry_points={
        'console_scripts': [
            'mochi = mochi.mochi:main'
        ]
    },
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers"
    ]
)
