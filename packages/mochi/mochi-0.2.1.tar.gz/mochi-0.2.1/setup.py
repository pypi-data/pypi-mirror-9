#!/usr/bin/env python
from setuptools import setup, find_packages
from mochi import __author__, __version__, __license__, GE_PYTHON_34

install_requires = ['rply>=0.7.3',
                    'pyrsistent>=0.9.3',
                    'greenlet>=0.4.5',
                    'eventlet>=0.17.2',
                    'pyzmq>=14.5.0',
                    'msgpack-python>=0.4.6',
                    'kazoo>=2.0',
                    'typeannotations>=0.1.0']

if not GE_PYTHON_34:
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
            'mochi = mochi.core:main'
        ]
    },
    packages=find_packages(),
    package_data = {
        'mochi': ['sexpressions/*',
                  'core/import_global_env.mochi',
                  'core/import_global_env_and_monkey_patch.mochi'],
    },
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
