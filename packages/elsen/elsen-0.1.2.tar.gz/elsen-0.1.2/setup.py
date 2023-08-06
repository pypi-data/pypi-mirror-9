#!/usr/bin/env python
from setuptools import setup, find_packages
import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = 'elsen/_version.py'
versioneer.versionfile_build = None
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'elsen-'
cmdclass = versioneer.get_cmdclass()

LONG_DESCRIPTION = open('README.md').read()

setup(
    name='elsen',
    version=versioneer.get_version(),
    author='Elsen Inc.',
    author_email='info@elsen.co',
    description='Elsen API Library',
    packages=find_packages(),
    data_files=[],
    entry_points={},
    install_requires=[
        'requests',
    ],
    long_description = LONG_DESCRIPTION,
    url="https://github.com/elsen-trading/examples/python",
    cmdclass=cmdclass
)
