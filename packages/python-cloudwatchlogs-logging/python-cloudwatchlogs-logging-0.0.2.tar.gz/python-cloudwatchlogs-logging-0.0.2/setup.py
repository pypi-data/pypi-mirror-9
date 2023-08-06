#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'python-cloudwatchlogs-logging',
          version = '0.0.2',
          description = '''Handler for easy logging to AWS CloudWatchLogs.''',
          long_description = '''
    Handler for easy logging to AWS CloudWatchLogs.
''',
          author = "Arne Hilmann",
          author_email = "arne.hilmann@gmail.com",
          license = 'Apache License 2.0',
          url = 'https://github.com/ImmobilienScout24/python-cloudwatchlogs-logging',
          scripts = [],
          packages = ['cloudwatchlogs_logging'],
          py_modules = [],
          classifiers = ['Development Status :: 2 - Pre-Alpha', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'Programming Language :: Python', 'Topic :: System :: Networking', 'Topic :: System :: Software Distribution', 'Topic :: System :: Systems Administration'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "boto", "docopt" ],
          
          zip_safe=True
    )
