#!/usr/bin/env python3
import re
import sys

from setuptools import setup, Command, find_packages


INIT_FILE = 'orbital/__init__.py'
init_data = open(INIT_FILE).read()

metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_data))

AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
LICENSE = metadata['license']
DESCRIPTION = metadata['description']

AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()

requires = ['numpy', 'scipy', 'astropy', 'matplotlib']


class PyTest(Command):
    """Allow 'python setup.py test' to run without first installing pytest"""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='OrbitalPy',
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README').read(),
    author=AUTHOR,
    author_email=EMAIL,
    url='https://github.com/RazerM/orbital',
    packages=find_packages(),
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    license=LICENSE,
    install_requires=requires)
