# -*- coding: utf-8 -*-
import logging

__author__ = 'Tim Schneider <tim.schneider@northbridge-development.de>'
__copyright__ = "Copyright 2015, Northbridge Development Konrad & Schneider GbR"
__credits__ = ["Tim Schneider", ]
__maintainer__ = "Tim Schneider"
__email__ = "mail@northbridge-development.de"
__status__ = "Development"

logger = logging.getLogger(__name__)


import os
from setuptools import setup, find_packages

#with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
#    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-splitdate',
    version='0.1.8',
    packages=find_packages(exclude=['*.tests',]),
    include_package_data=True,
    install_requires=['Django >=1.7',],
    license='MIT License',
    description='A widget for django form date fields that displays three inputs (day, month, year).',
    #long_description=README,
    url='http://github.com/NB-Dev/django-splitdate',
    author='Nothrbridge Development Konrad & Schneider GbR',
    author_email='mail@nb-dev.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)