#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2012 Ilya Shalyapin
#  Copyright (c) 2015 Jesús Espino
#
#  django-transactional-cleanup is free software under terms of the MIT License.
#

import os
from setuptools import setup, find_packages


setup(
    name     = 'django-transactional-cleanup',
    version  = '0.1.11',
    packages = ['django_transactional_cleanup',],
    include_package_data=True,
    requires = ['python (>= 2.7)', 'django (>= 1.6.1)'],
    install_requires = ['django-transaction-hooks >= 0.2'],
    description  = 'Deletes old files on transaction commit.',
    long_description = open('README.markdown').read(),
    author       = 'Jesús Espino',
    author_email = 'jesus.espino@kaleidos.net',
    url          = 'https://github.com/jespino/django-transactional-cleanup',
    download_url = 'https://github.com/jespino/django-transactional-cleanup/tarball/master',
    license      = 'MIT License',
    keywords     = 'django',
    classifiers  = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
