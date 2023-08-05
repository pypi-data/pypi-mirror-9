# -*- coding: utf-8 -*-
import codecs
import os

from setuptools import setup


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts),
                       encoding='utf-8').read()


classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Testing',
    'Topic :: Text Processing :: Markup :: XML'
]

setup(name='xmlunittestbetter',
      version='0.1',
      description=(
          'Library using lxml and unittest for unit testing XML. '
          'This is an actively maintained and PEP8 compliant '
          'fork of xmlunittest.'),
      long_description=read('README.md'),
      author='Richard O\'Dwyer',
      author_email='richard@richard.do',
      license='MIT',
      url='https://github.com/richardasaurus/python-xmlunittest-better',
      py_modules=['xmlunittest'],
      install_requires=['lxml>=2.3,<3.4.0'],
      classifiers=classifiers)
