#!/usr/bin/env python

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='tornadwwo',
      version='0.1.3',
      description='Async API calls for World Weather Online',
      keywords='tornado weather non-blocking api http',
      author='ALIANE Abdenour Abdelouahab',
      author_email='abdelouahab_al@yahoo.fr',
      url='https://github.com/abdelouahabb/tornadwwo',
      packages=['tornadwwo'],
      install_requires=["tornado"],
      setup_requires=["tornado"],
      license='MIT',
     )
