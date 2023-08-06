#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
import os

long_description = ""
for doc_file in ('installation.rst', 'usage.rst', 'changelog.rst'):
    with open(os.path.join('docs', doc_file)) as file:
        long_description += file.read()

setup(name='py-romanify',
      version='0.1.3',
      description='Python Roman/Arabic numerals convertor',
      long_description=long_description,
      author='Peter Lisak',
      author_email='peter.lisak+pypi@gmail.com',
      url='https://github.com/peter-lisak/py-romanify',
      packages=['romanify'],
      test_suite="tests",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)', 
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.1',          
          'Programming Language :: Python :: 3.2',          
          'Programming Language :: Python :: 3.3',          
          'Programming Language :: Python :: 3.4',          
          'Topic :: Education',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          ],
      keywords='convertor roman arabic numerals numbers',
      license="GNU GENERAL PUBLIC LICENSE"
     )

