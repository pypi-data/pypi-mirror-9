#!/usr/bin/env python2

from distutils.core import setup

from fftresize import fftresize


_classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: ISC License (ISCL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Topic :: Multimedia :: Graphics',
]

with open('README.rst', 'r') as rst_file:
    _long_description = rst_file.read()

_setup_args = {
    'author':           fftresize.__author__,
    'author_email':     fftresize.__email__,
    'classifiers':      _classifiers,
    'description':      fftresize.__doc__,
    'license':          fftresize.__license__,
    'long_description': _long_description,
    'name':             'FFTresize',
    'url':              'https://bitbucket.org/eliteraspberries/fftresize',
    'version':          fftresize.__version__,
}


if __name__ == '__main__':

    setup(packages=['avena', 'fftresize'], scripts=['scripts/fftresize'],
          **_setup_args)
