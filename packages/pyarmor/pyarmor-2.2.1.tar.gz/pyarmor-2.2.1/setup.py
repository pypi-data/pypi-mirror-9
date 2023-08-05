#!/usr/bin/env python
#

import sys
import os
from distutils.core import setup

def get_description():
    README = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pyarmor.rst'))
    f = open(README, 'r')
    try:
        return f.read()
    finally:
        f.close()

VERSION = '2.2.1'

def main():
    args = dict(
        name='pyarmor',
        version=VERSION,
        description='A python package could import/run encrypted python scripts.',
        long_description=get_description(),
        keywords=['encrypt', 'distribute', 'pyinstaller'],
        py_modules=['pyarmor', 'pyimcore', 'wizard'],
        author='Jondy Zhao',
        author_email='jondy.zhao@gmail.com',
        maintainer='Jondy Zhao',
        maintainer_email='jondy.zhao@gmail.com',
        url='http://dashingsoft.com/products/pyarmor.html',
        platforms=['Windows', 'Linux'],
        license='Shareware',
        )
    setup(**args)

if __name__ == '__main__':
    main()
