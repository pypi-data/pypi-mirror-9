#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'isphere',
          version = '0.0.1',
          description = '''interactive shell for vsphere''',
          long_description = '''isphere - interactive shell for vsphere''',
          author = "Maximilien Riehl",
          author_email = "max@riehl.io",
          license = 'WTFPL',
          url = 'https://github.com/mriehl/isphere',
          scripts = ['scripts/isphere'],
          packages = ['thirdparty', 'isphere', 'isphere.command'],
          py_modules = [],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'Programming Language :: Python', 'Topic :: System :: Systems Administration'],
          entry_points={
          'console_scripts':
              ['isphere.exe = isphere.cli:main']
          },
             #  data files
             # package data
          install_requires = [ "cmd2", "docopt", "pyvmomi" ],
          
          zip_safe=True
    )
