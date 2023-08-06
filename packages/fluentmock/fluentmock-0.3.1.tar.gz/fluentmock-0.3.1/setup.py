#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'fluentmock',
          version = '0.3.1',
          description = '''Fluent interface facade for Michael Foord's mock.''',
          long_description = '''Please visit https://github.com/aelgru/fluentmock''',
          author = "Michael Gruber",
          author_email = "aelgru@gmail.com",
          license = 'Apache License, Version 2.0',
          url = 'https://github.com/aelgru/fluentmock',
          scripts = [],
          packages = ['fluentmock'],
          py_modules = [],
          classifiers = ['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.2', 'Programming Language :: Python :: 3.3', 'Programming Language :: Python :: 3.4', 'Topic :: Software Development :: Testing', 'Topic :: Software Development :: Quality Assurance'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
          package_data = {'fluentmock': ['LICENSE.txt']},   # package data
          install_requires = [ "mock" ],
          
          zip_safe=True
    )
