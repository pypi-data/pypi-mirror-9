#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# author: Manuel Guenther <manuel.guenther@idiap.ch>
# date:   Wed Feb 13 12:35:29 CET 2013

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='bob.db.youtube',
    version=version,
    description='Youtube Faces Database Access API for Bob',
    url='http://github.com/bioidiap/bob.db.youtube',
    license='GPLv3',
    author='Manuel Guenther',
    author_email='manuel.guenther@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
      'setuptools',
      'six',  # py2/3 compatibility library
      'bob.io.base',
      'bob.io.matlab', # to read MatLab files of the original protocol
      'bob.db.base',
      'bob.db.verification.utils' # defines a set of utilities for face verification databases like this one.
    ],

    namespace_packages = [
      'bob',
      'bob.db',
    ],

    entry_points = {
      # bob database declaration
      'bob.db': [
        'youtube = bob.db.youtube.driver:Interface',
      ],
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
    ],
)
