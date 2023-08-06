#!/usr/bin/env python

import sys
import os
from distutils.core import setup, Extension

def get_description():
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'README.md'))
    f = open(filename, 'r')
    try:
        return f.read()
    finally:
        f.close()

VERSION = '0.1.3'

def main():
    setup_args = dict(
        name='python-ddd',
        version=VERSION,
        description='python-ddd is a super-GDB debugger ' \
                    'used to debug python scripts line by line in GDB',
        long_description=get_description(),
        keywords=['debug', 'gdb', 'pdb'],
        py_modules=['libddd'],
        author='Jondy Zhao',
        author_email='jondy.zhao@gmail.com',
        maintainer='Jondy Zhao',
        maintainer_email='jondy.zhao@gmail.com',
        url='https://github.com/jondy/pyddd',
        platforms=['Windows', 'Linux'],
        license='GPLv3',
        )
    setup_args['ext_modules'] = [Extension('ipa', sources=['ipa.c'],)]
    setup(**setup_args)

if __name__ == '__main__':
    main()
