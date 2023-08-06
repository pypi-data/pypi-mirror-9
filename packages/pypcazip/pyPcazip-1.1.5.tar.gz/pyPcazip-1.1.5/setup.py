#!/usr/bin/env python
""" Setup script. Used by easy_install and pip. """

import os

from distutils.core import setup
from setuptools import find_packages

import sys
import textwrap

'''The minimum version of NumPy required.'''
min_numpy_version = '1.0.3'
min_scipy_version = '0.10.0'

'''Some functions for showing errors and warnings.'''
def _print_admonition(kind, head, body):
    tw = textwrap.TextWrapper(
        initial_indent='   ', subsequent_indent='   ')

    print ".. %s:: %s" % (kind.upper(), head)
    for line in tw.wrap(body):
        print line

def exit_with_error(head, body=''):
    _print_admonition('error', head, body)
    sys.exit(1)

def print_warning(head, body=''):
    _print_admonition('warning', head, body)

print "Checking python version!"
if not (sys.version_info[0] >= 2 and sys.version_info[1] >= 4):
    exit_with_error("You need Python 2.4 or greater to install pyPcazip!")
print "Python version checked."

''' Check for required Python packages. '''
def check_import(pkgname, pkgver):
    try:
        mod = __import__(pkgname)
    except ImportError:
        exit_with_error(
            "Can't find a local %s Python installation." % pkgname,
            "Please read carefully the ``README`` file "
            "and remember that pyPcazip needs the %s package "
            "to compile and run." % pkgname )
    else:
        if mod.__version__ < pkgver:
            exit_with_error(
                "You need %(pkgname)s %(pkgver)s or greater to run pyPcazip!"
                % {'pkgname': pkgname, 'pkgver': pkgver} )

    print ( "* Found %(pkgname)s %(pkgver)s package installed."
            % {'pkgname': pkgname, 'pkgver': mod.__version__} )
    globals()[pkgname] = mod
    
check_import('numpy', min_numpy_version)
check_import('scipy', min_scipy_version)

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup_args = {
    'name'             : "pyPcazip",
    'version'          : "1.1.5",
    'description'      : "PCA-based trajectory file compression and analysis.",
    'long_description' : "PCA-based trajectory file compression and analysis.",
    'author'           : "The University of Nottingham & BSC",
    'url'              : "https://bitbucket.org/ramonbsc/pypcazip/overview",
    'download_url'     : "https://bitbucket.org/ramonbsc/pypcazip/get/1.1.5.tar.gz",
    'license'          : "BSD license or similar.",
    'classifiers'      : [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

    'namespace_packages': ['MDPlus','CoRe'],
    'packages'    : find_packages('src'),
    'package_dir' : {'': 'src'},
    'scripts' : ['src/pyPcazip',
                 'src/pyPcaunzip',
                 'src/pyPczcomp',
                 'src/pyPczdump',
                 'src/pyPczplot',
                 'src/pyPczclust'],
    'install_requires' : ['numpy',
                          'scipy',
    		          'MDAnalysis',
                          'argh'],
    'extras_require': {'PCZ7': ['h5py'],
                       'BINPOS': ['mdtraj'],
                       'ALL': ['h5py',
                               'mdtraj'],
                       },

    'zip_safe'         : False,
}

setup(**setup_args)
