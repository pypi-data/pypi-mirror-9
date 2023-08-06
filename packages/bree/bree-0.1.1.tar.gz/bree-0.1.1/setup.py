# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

import sys
import bree

# python3
#backports.ssl-match-hostname


options = dict(
    name="bree",
    version=bree.version,
    packages=['bree'],
    description="a micro library for happy coding tornado.",
    author='WANG WENPEI',
    author_email="wangwenpei@nextoa.com",
    install_requires=['tornado', 'certifi', 'cliez'],
    include_package_data=True,
    download_url='https://github.com/nextoa/bree/archive/master.zip',
    license='http://opensource.org/licenses/MIT',
    keywords='tornado'
)

if sys.version_info > (3, 0):
    options['install_requires'].append('backports.ssl-match-hostname')

setup(**options)


