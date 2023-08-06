#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
        name = '36ban_commons',
        version = '0.0.1',
        keywords = ('36ban', 'commons'),
        description = 'eking commons',
        license = 'MIT License',

        url = 'http://liluo.org',
        author = 'zhaowenlei',
        author_email = 'zhaowenlei789@sina.com',

        packages = find_packages(),
        include_package_data = True,
        platforms = 'any',
        install_requires = [],
)
