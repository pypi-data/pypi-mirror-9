#!/usr/bin/env python2

from distutils.core import setup

from hipshot import hipshot


_classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: ISC License (ISCL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Multimedia :: Video',
]

with open('README.rst', 'r') as file:
    _long_description = file.read()

_setup_args = {
    'author':           hipshot.__author__,
    'author_email':     hipshot.__email__,
    'classifiers':      _classifiers,
    'description':      hipshot.__doc__,
    'license':          hipshot.__license__,
    'long_description': _long_description,
    'name':             'Hipshot',
    'url':              'https://bitbucket.org/eliteraspberries/hipshot',
    'version':          hipshot.__version__,
}


if __name__ == '__main__':

    setup(packages=['avena', 'hipshot'], scripts=['scripts/hipshot'],
          **_setup_args)
