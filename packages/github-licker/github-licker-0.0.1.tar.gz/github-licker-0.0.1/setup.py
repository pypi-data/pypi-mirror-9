#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'github-licker',
          version = '0.0.1',
          description = '''Licker - Your Github License Checker for Organisational Repositories.''',
          long_description = '''
    Using the Github API v3 including the [Licenses API](https://developer.github.com/v3/licenses/) developer preview,
    Licker is able to check licenses of all repositories in your Github organisation. It helps especially identifying
    repos without license file.
    ''',
          author = "Jan Brennenstuhl",
          author_email = "jan@brennenstuhl.me",
          license = 'Apache License 2.0',
          url = 'https://github.com/jbspeakr/github-licker',
          scripts = ['scripts/licker'],
          packages = ['licker'],
          py_modules = [],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'Programming Language :: Python :: 3 :: Only'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "docopt" ],
          
          zip_safe=True
    )
