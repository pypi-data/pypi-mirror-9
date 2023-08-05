#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='WebPocket',
      version='0.1.2',
      description='Actor-model based WebSocket client in Python',
      long_description='Actor-model based WebSocket client in Python',
      author='xhs',
      author_email='chef@dark.kitchen',
      url='https://github.com/xhs/WebPocket/',
      packages=['webpocket'],
      platforms=["any"],
      license='BSD',
      install_requires=['Twisted', 'service_identity'])
