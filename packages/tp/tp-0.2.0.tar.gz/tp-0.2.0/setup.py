#!/usr/bin/env python
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

exec(read('tp/version.py'))

setup(name='tp',
      version=version_string,
      description='TargetProcess API wrapper',
      long_description=read('README.md'),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],
      keywords='targetprocess rest api wrapper',
      url='http://github.com/eduarbo/tp.py',
      author='Eduardo Ruiz',
      author_email='eduarbo@gmail.com',
      license='Apache 2.0',
      packages=['tp'],
      install_requires=[
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False
      )
