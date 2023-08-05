#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

setup(

    name='bob.db.iris',
    version=version,
    description='Bob access API for Fisher\'s Iris Flower Dataset',
    url='http://github.com/bioidiap/bob.db.iris',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
      'setuptools',
      'bob.io.base',
      'bob.measure',
      'bob.learn.linear',
      'bob.db.base',
      'matplotlib',
    ],

    namespace_packages=[
      "bob",
      "bob.db",
    ],

    entry_points={
      'console_scripts': [
        'iris_lda.py = bob.db.iris.example.lda:main',
      ],

      'bob.db': [
        'iris = bob.db.iris.driver:Interface',
      ],
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
