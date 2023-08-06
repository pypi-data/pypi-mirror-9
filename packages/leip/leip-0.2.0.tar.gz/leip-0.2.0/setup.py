#!/usr/bin/env python

import sys
from setuptools import setup

DESCRIPTION = "Ultralightweight python CLI framework"

entry_points = {
    'console_scripts': [
        'leip = leip.cli:dispatch'
    ]}

setup(name='leip',
      version='0.2.0',
      description=DESCRIPTION,
      author='Mark Fiers',
      entry_points=entry_points,
      author_email='mark.fiers.42@gmail.com',
      url='http://mfiers.github.com/Leip',
      packages=['leip'],
      include_package_data=True,
      package_dir={'': 'src'},
      requires=[
          'fantail',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ]
      )
