#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from setuptools import setup, find_packages
import os


ROOT_PACKAGE = 'django-webdav-storage'
DIR = os.path.dirname(__file__)
VERSION = '0.4'
DESCRIPTION = ('This application allows you easily save media and static '
               'files into webdav storage')


def long_description():
    """
    Returns package long description from README
    """
    def read(what):
        with open(os.path.join(DIR, '%s.rst' % what)) as fp:
            return fp.read()
    return '{README}\n'.format(README=read('README'))


def version():
    """
    Returns package version for package building
    """
    return VERSION


if __name__ == '__main__':
    setup(name=ROOT_PACKAGE,
          description=DESCRIPTION,
          author='Mikhail Porokhovnichenko',
          author_email='marazmiki@gmail.com',
          url='https://github.com/marazmiki/django-webdav-storage',
          version=version(),
          long_description=long_description(),
          packages=find_packages(),
          include_package_data=True,
          test_suite='tests.main',
          install_requires=['requests'],
          tests_require=['requests'],
          zip_safe=False,
          classifiers=[
              'Environment :: Web Environment',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
              'Framework :: Django'
          ],
    )
