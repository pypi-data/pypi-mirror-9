#!/usr/bin/env python
# coding=utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'simplefetion',
    version = '0.0.5',
    description = 'Simple Fetion: send message / group messages',
    author = 'Cole Smith',
    author_email = 'uniquecolesmith@gmail.com',
    url = 'https://djangofetion.sinaapp.com/',
    packages = ['simplefetion'],
    include_package_data = True,
    install_requires = ['requests', 'BeautifulSoup4', ],
    zip_safe = False,
    classifiers = (
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)
