#!/usr/bin/env python

PROJECT = 'virtualenvwrapper.djangodeploy'
VERSION = '1.0.0'

from setuptools import setup, find_packages

try:
    long_description = open('README', 'rt').read()
except IOError:
    long_description = ''

description = ('virtualenvwrapper plugin to '
               'create a Django deploy work directory')

setup(
    name=PROJECT,
    version=VERSION,

    description=description,
    long_description=long_description,

    author='Tino de Bruijn',
    author_email='tinodb@gmail.com',

    url='https://github.com/tino/virtualenvwrapper.djangodeploy',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Framework :: Django',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    platforms=['Any'],
    provides=['virtualenvwrapper.djangodeploy'],
    requires=['virtualenv',
              'virtualenvwrapper (>=4.0)',
              ],
    namespace_packages=['virtualenvwrapper'],
    packages=find_packages(),
    entry_points={
        'virtualenvwrapper.project.template': [
            'djangodeploy = virtualenvwrapper.django_deploy:template',
        ],
    },
    include_package_data=True,
)
