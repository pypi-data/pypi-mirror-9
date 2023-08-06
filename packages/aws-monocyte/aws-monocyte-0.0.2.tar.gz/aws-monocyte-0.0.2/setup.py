#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'aws-monocyte',
          version = '0.0.2',
          description = '''Monocyte - Search and Destroy unwanted AWS Resources relentlessly.''',
          long_description = '''
    Monocyte is a bot for destroying AWS resources in non-EU regions written in Python using Boto.
    It is especially useful for companies that are bound to European privacy laws
    and for that reason don't want to process user data in non-EU regions.
    ''',
          author = "Jan Brennenstuhl, Arne Hilmann",
          author_email = "jan@brennenstuhl.me, arne.hilmann@gmail.com",
          license = 'Apache License 2.0',
          url = 'https://github.com/ImmobilienScout24/aws-monocyte',
          scripts = ['scripts/monocyte'],
          packages = ['monocyte', 'monocyte.handler'],
          py_modules = [],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'Programming Language :: Python', 'Topic :: System :: Networking', 'Topic :: System :: Software Distribution', 'Topic :: System :: Systems Administration'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "boto", "docopt", "python-cloudwatchlogs-logging" ],
          
          zip_safe=True
    )
