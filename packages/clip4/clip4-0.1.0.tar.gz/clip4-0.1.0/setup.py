#!/usr/bin/env python3
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from setuptools import setup

setup(name='clip4',
      version='0.1.0',
      description='A clipboard command line program shared with Dropbox',
      url='https://github.com/yumaokao/clip4',
      author='yumaokao',
      author_email='ymkq9h@gmail.com',
      license='MIT',
      packages=['clip4'],
      entry_points={
          'console_scripts':
              ['clip4 = clip4.main:main']
      },
      install_requires=[
          'dropbox'
      ],
      zip_safe=False)
