# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

import fabez

setup(
    name='fabez',
    version=fabez.version,
    packages=['fabez'],
    url='https://github.com/baixing/cabric',
    download_url='https://github.com/baixing/cabric/tarball/master',
    license='http://opensource.org/licenses/MIT',
    install_requires=[
        'fabric',
        'cliez',
        'pyyaml'
    ],
    author='Breeze.Kay',
    author_email='wangwenpei@nextoa.com',
    description='A deploy tool for CentOS, based on fabric. for new version,you should use cabric',
    keywords='fabric,fabez,cabric',
    package_data={
        'fabez': ['tpl/*.*', 'tpl/web/*']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fabez = fabez.main:main',
            # 'cabric = fabez.web:main'
        ]
    },

)

