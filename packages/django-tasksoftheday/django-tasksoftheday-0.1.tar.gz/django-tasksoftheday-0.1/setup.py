# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:05:28 2015

@author: simon
"""

import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tasksoftheday',
    version='0.1',
    packages=['tasksoftheday'],
    include_package_data=True,
    license='MIT License',  # example license
    description='A simple Django app for task tracking.',
    long_description=README,
    url='http://www.example.com/',
    author='Simon Lenz',
    author_email='dev@simon-lenz.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        #'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
