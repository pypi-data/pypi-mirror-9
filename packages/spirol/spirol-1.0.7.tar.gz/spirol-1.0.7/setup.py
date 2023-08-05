#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

#    Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

import spirol
import versioneer
product = 'spirol'

versioneer.VCS = 'git'
versioneer.versionfile_source = '%s/version.py' % product
versioneer.versionfile_build = '%s/version.py' % product
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = '%s-' % product

history_path = history = 'HISTORY.rst'
try:
    open(history_path).read()
except IOError:
    open(history_path, 'w').write('')

setup(
    name=product,
    packages=find_packages(exclude=('tests',)),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url=spirol.__url__,
    author=spirol.__author__,
    author_email=spirol.__email__,
    description=spirol.__short_description__,
    long_description=open('README.md').read() + open(history_path).read(),
    license=open('LICENCE').readlines()[1].strip(),
    platforms=['any'],
    classifiers=[k for k in open('CLASSIFIERS').read().split('\n') if k],
    zip_safe=False,
    install_requires=[k for k in open('requirements.txt').readlines() if k],
    keywords='algorithms',
)
