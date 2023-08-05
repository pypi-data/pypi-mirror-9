#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'committer',
          version = '0.2.7',
          description = '''Unified command line interface for git, mercurial and subversion.''',
          long_description = '''Please visit https://github.com/aelgru/committer for more information!''',
          author = "Michael Gruber",
          author_email = "aelgru@gmail.com",
          license = 'Apache License, Version 2.0',
          url = 'https://github.com/aelgru/committer',
          scripts = ['ci', 'st', 'up'],
          packages = ['committer', 'committer.vcsclients'],
          py_modules = [],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.0', 'Programming Language :: Python :: 3.1', 'Programming Language :: Python :: 3.2', 'Programming Language :: Python :: 3.3', 'Programming Language :: Python :: 3.4', 'Topic :: Software Development :: User Interfaces', 'Topic :: Software Development :: Version Control', 'Topic :: Utilities'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
          package_data = {'committer': ['LICENSE.txt']},   # package data
          
          
          zip_safe=True
    )
