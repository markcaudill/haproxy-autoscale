#!/usr/bin/env python

from setuptools import setup

setup(name='haproxy-autoscale',
      version='0.4.1',
      description='HAProxy wrapper for handling auto-scaling EC2 instances.',
      author='Mark Caudill',
      author_email='mark@markcaudill.me',
      url='https://github.com/markcaudill/haproxy-update',
      install_requires=['boto>=2.9', 'mako>=0.5.0', 'argparse>=1.2.1'],
      license='MIT'
      )
