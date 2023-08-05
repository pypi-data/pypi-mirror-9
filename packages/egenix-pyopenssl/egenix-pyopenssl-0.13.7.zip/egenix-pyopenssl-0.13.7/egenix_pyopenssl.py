#!/usr/local/bin/python
# -*- coding: latin-1 -*-

""" Configuration for the eGenix pyOpenSSL Distribution

    Copyright (c) 2008-2014, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
import glob, os, sys
import mxSetup
from mxSetup import mx_Extension, mx_version, find_file, parse_mx_version

#
# Check Python version
#
if sys.version[:3] < '2.3':
    raise TypeError('pyOpenSSL needs at least Python version 2.3')

#
# Package version
#
# Note that we no longer include the OpenSSL version in the package
# number. When updating OpenSSL, please also edit extras/load_openssl.py.
#
_openssl_version = '1.0.1k'
version = mx_version(0, 13, 7,
                     snapshot=0,
                     pep_compatible=1)
#print version

#
# Setup information
#
name = "egenix-pyopenssl"

#
# Meta-Data
#
description = "eGenix pyOpenSSL Distribution for Python"
long_description = """\
eGenix pyOpenSSL Distribution for Python
----------------------------------------

The eGenix.com pyOpenSSL Distribution includes everything you need to
get started with OpenSSL in Python, based on the fine pyOpenSSL
package that is available from Launchpad at
https://launchpad.net/pyopenssl/.

It comes with an easy to use installer that includes the most recent
OpenSSL library versions in pre-compiled form and also ships with the
most recent certificate authority (CA) bundles from Mozilla, together
with a support module to make using the bundles easy in pyOpenSSL.

You can also compile pyOpenSSL yourself. For Windows, we include all
necessary OpenSSL build files to make this easy for you. On other
platforms, you just need to install the OpenSSL library (including the
development headers) to compile from source.

Downloads
---------

For downloads, documentation, installation instructions, changelog,
and feature list, please visit the product page at:

    http://www.egenix.com/products/python/pyOpenSSL/

Web Installer
-------------

The source package on the Python Package Index (PyPI) is a web
installer, which will automatically select and download the right
binary package for your installation platform.

This source package does not include the crypto code, so it's safe to
download and distribute. Before downloading the crypto code archives,
the web installer will ask for confirmation of the export regulations
that apply to the code.

For more information, please see

    http://www.egenix.com/products/python/pyOpenSSL/#WebInstaller

Licenses
--------

pyOpenSSL was originally written by Martin Sjoegren for AB Strakt and
is now maintained by Jean-Paul Calderone.

This distribution is brought to you by eGenix.com and made available
under the eGenix.com Public License 1.1.0.

pyOpenSSL is distributed under the Apache License 2.0.

OpenSSL is distributed under the OpenSSL license.

This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com).  This product includes software written by Tim
Hudson (tjh@cryptsoft.com).  This product includes software developed
by the OpenSSL Project for use in the OpenSSL
Toolkit. (http://www.openssl.org/)
"""
license = (
"eGenix.com Public License 1.1.0; "
"Copyright (c) 2008-2014, eGenix.com Software GmbH, All Rights Reserved"
)
author = "eGenix.com Software GmbH"
author_email = "info@egenix.com"
maintainer = "eGenix.com Software GmbH"
maintainer_email = "info@egenix.com"
url = "http://www.egenix.com/products/python/pyOpenSSL/"
download_url = 'https://downloads.egenix.com/python/download_url/%s/%s/' % (
    name,
    version)
platforms = [
    'Windows',
    'Linux',
    'Mac OS X',
#    'FreeBSD',
#    'Solaris',
#    'AIX',
    ]
classifiers = [
    "Environment :: Console",
    "Environment :: No Input/Output (Daemon)",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Python License (CNRI Python License)",
    "License :: Freely Distributable",
    "License :: Other/Proprietary License",
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: BeOS",
    "Operating System :: MacOS",
    "Operating System :: OS/2",
    "Operating System :: Other OS",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Communications",
    "Topic :: Documentation",
    "Topic :: Internet",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities ",
    ]
if 'a' in version:
    classifiers.append("Development Status :: 3 - Alpha")
elif 'b' in version:
    classifiers.append("Development Status :: 4 - Beta")
else:
    classifiers.append("Development Status :: 5 - Production/Stable")
    classifiers.append("Development Status :: 6 - Mature")
classifiers.sort()

#
# Data files
#
data_files = [

    # Distribution copyright, license and READMEs
    ('README', 'OpenSSL/'),
    ('LICENSE', 'OpenSSL/'),
    ('COPYRIGHT', 'OpenSSL/'),

    # Other copyrights, licenses, READMEs
    ('LICENSE.pyOpenSSL', 'OpenSSL/'),
    ('LICENSE.OpenSSL', 'OpenSSL/'),
    ('LICENSE.zlib', 'OpenSSL/'),
    ('EXPORT-TERMS', 'OpenSSL/'),
    ('pyOpenSSL/LICENSE', 'OpenSSL/pyOpenSSL/'),
    ('pyOpenSSL/ChangeLog', 'OpenSSL/pyOpenSSL/'),
    ('pyOpenSSL/README', 'OpenSSL/pyOpenSSL/'),
    ('pyOpenSSL/TODO', 'OpenSSL/pyOpenSSL/'),

    # CA certificates
    ('ca-bundle.crt', 'OpenSSL/'),
    ('ca-bundle-server.crt', 'OpenSSL/'),
    ('ca-bundle-email.crt', 'OpenSSL/'),
    ('ca-bundle-codesigning.crt', 'OpenSSL/'),

    ]

#
# Python packages
#
packages = [

    # OpenSSL package
    'OpenSSL',
    'OpenSSL.test',

    ]

#
# C Extensions
#

# Compile time symbols to always #define
_openssl_defines = [
    # Always try loading the openssl.conf file when initializing OpenSSL;
    # this allows configuration changes to be applied without having
    # to manipulate the application using OpenSSL.
    ('OPENSSL_LOAD_CONF', None),
    ]

if sys.platform == 'win32':
    # Windows environments
    
    # Use the SSL environ variable to find the OpenSSL build directory
    _openssl_dir = os.environ.get('SSL', None)
    if _openssl_dir is None:
        # fall back to the included OpenSSL DLLs
        if sys.version[:3] <= '2.3':
            _openssl_dir = os.path.join('openssl-win32', 'vc6')
        elif sys.version[:3] <= '2.5':
            _openssl_dir = os.path.join('openssl-win32', 'vc7')
        elif sys.version[:3] >= '2.6':
            if sys.maxsize > 2L**32:
                _openssl_dir = os.path.join('openssl-win64', 'vc9')
            else:
                _openssl_dir = os.path.join('openssl-win32', 'vc9')
        else:
            raise ValueError('no SSL environment variable defined; '
                             'please setup SSL to point to the OpenSSL '
                             'build directory')
        
    _needed_includes=[('openssl/ssl.h',
                       [os.path.join(_openssl_dir, 'inc32'),
                        os.path.join(_openssl_dir)],
                       'The OpenSSL Project')]
    _needed_libraries=[('libeay32',
                        [os.path.join(_openssl_dir, 'out32dll')],
                        'OpenSSL'),
                       ('ssleay32',
                        [os.path.join(_openssl_dir, 'out32dll')],
                        'OpenSSL'),
                       ]
    _libraries = ['ws2_32']
    _data_files = [
        (os.path.join(_openssl_dir, 'out32dll', 'openssl.exe'), 'OpenSSL/'),
        ]
    
    # We always want the DLLs to be included in the OpenSSL/ package
    _include_needed_libraries = 1

else:
    # Unix environments:
    if sys.maxint > 2L**32:
        _lib_dir = 'lib64'
    else:
        _lib_dir = 'lib'

    # Use the SSL environ variable to find the OpenSSL build directory
    _openssl_dir = os.environ.get('SSL', '/usr/local/ssl')
    _needed_includes=[('openssl/ssl.h',
                       [os.path.join(_openssl_dir, 'include'),
                        '/usr/local/ssl/include',
                        '/usr/ssl/include'],
                       'The OpenSSL Project')]
    _needed_libraries=[('crypto',
                        [os.path.join(_openssl_dir, _lib_dir),
                         '/usr/local/ssl/lib',
                         '/usr/ssl/lib'],
                        'OpenSSL'),
                       ('ssl',
                        [os.path.join(_openssl_dir, _lib_dir),
                         '/usr/local/ssl/lib',
                         '/usr/ssl/lib'],
                        'OpenSSL')]
    _libraries = []
    _openssl_bin_dir = find_file('openssl',
                                 [os.path.join(_openssl_dir, 'bin'),
                                  '/usr/local/ssl/bin',
                                  '/usr/ssl/bin',
                                  '/usr/bin'])
    if not _openssl_bin_dir:
        raise ValueError('no SSL environment variable defined; '
                         'please setup SSL to point to the OpenSSL '
                         'directory')
    _data_files = [
        (os.path.join(_openssl_bin_dir, 'openssl'), 'OpenSSL/'),
        ]

    # IMPORTANT NOTE:
    #
    # We try to always include the OpenSSL shared libs with the
    # package, since there are too many different versions installed
    # on various OSes and many of them have compatibility problems
    # (e.g.  a few macros changed to functions from 0.9.8d to 0.9.8e).
    #
    # However, this introduces another problem: the linker has to find
    # the needed shared libraries, since on Unix the linker does not
    # look in the same directory as the parent .so file when looking
    # for dependencies (unlike on Windows).
    #
    # Because of this, we use a trick in OpenSSL/__init__.py to
    # explicitly load the included shared libs for OpenSSL. If this
    # fails for some reason (it needs either ctypes or mxTools installed
    # and the OS has to support the dlopen() function), include the
    # OpenSSL/ directry in the LD_LIBRARY_PATH environment variable
    # *before* starting the Python process.
    #
    _include_needed_libraries = 1
    
ext_modules = [

    mx_Extension('OpenSSL.crypto',
                 glob.glob(os.path.join('OpenSSL','crypto','*.c')) +
                 glob.glob(os.path.join('OpenSSL','*.c')),
                 define_macros=_openssl_defines,
                 include_dirs=[os.path.join('OpenSSL','crypto'),
                               os.path.join('OpenSSL')],
                 needed_includes=_needed_includes,
                 needed_libraries=_needed_libraries,
                 include_needed_libraries=_include_needed_libraries,
                 libraries=_libraries,
                 ),

    mx_Extension('OpenSSL.rand',
                 glob.glob(os.path.join('OpenSSL','rand','*.c')) +
                 glob.glob(os.path.join('OpenSSL','*.c')),
                 define_macros=_openssl_defines,
                 include_dirs=[os.path.join('OpenSSL','rand'),
                               os.path.join('OpenSSL')],
                 needed_includes=_needed_includes,
                 needed_libraries=_needed_libraries,
                 include_needed_libraries=_include_needed_libraries,
                 libraries=_libraries,
                 ),

    mx_Extension('OpenSSL.SSL',
                 glob.glob(os.path.join('OpenSSL','ssl','*.c')) +
                 glob.glob(os.path.join('OpenSSL','*.c')),
                 define_macros=_openssl_defines,
                 include_dirs=[os.path.join('OpenSSL','ssl'),
                               os.path.join('OpenSSL')],
                 needed_includes=_needed_includes,
                 needed_libraries=_needed_libraries,
                 include_needed_libraries=_include_needed_libraries,
                 libraries=_libraries,
                 # Only include this once
                 data_files=_data_files,
                 ),

    ]

