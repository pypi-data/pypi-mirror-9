#!/usr/bin/env python

from setuptools import setup, find_packages
from cloudfs.private.cloudfs_paths import cloudfs_version

setup(name='cloudfs_sdk',
      version=cloudfs_version,
      description='Python SDK for CloudFS cloud storage file system.',
      license='MIT',
      author='Bitcasa Inc.',
      author_email='drex@bitcasa.com',
      url='https://www.bitcasa.com/cloudfs',
      keywords='cloud storage filesystem',
      packages=find_packages(exclude=['test*']),
      install_requires=['requests>=2.4.3'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Topic :: Other/Nonlisted Topic'
      ]
     )