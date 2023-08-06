#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
        name = 'zhaowenlei',
        version = '0.0.1',
        keywords = ('zhaowenlei', 'egg'),
        description = 'a simple zhaowenlei egg',
        license = 'MIT License',

        url = 'http://liluo.org',
        author = 'zhaowenlei',
        author_email = 'zhaowenlei789@sina.com',

        packages = find_packages(),
        include_package_data = True,
        platforms = 'any',
        install_requires = [],
)
