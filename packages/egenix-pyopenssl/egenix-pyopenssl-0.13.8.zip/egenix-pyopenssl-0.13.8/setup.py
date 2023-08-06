#!/usr/bin/env python

""" Distutils Setup File for the eGenix pyOpenSSL distribution.

"""
#
# Run web installer, if needed
#
import mxSetup, os, sys
# Package directory
dirname = os.path.dirname(os.path.abspath(__file__))
# Read export terms
f = open(os.path.join(dirname, 'EXPORT-TERMS'), 'r')
terms = f.read()
f.close()
# Run web installer
mxSetup.run_web_installer(
    dirname,
    landmarks=('OpenSSL', 'PREBUILT'),
    web_installer_class=mxSetup.CryptoWebInstaller,
    terms=terms)

#
# Load configuration(s)
#
import egenix_pyopenssl
configurations = (egenix_pyopenssl,)

#
# Run distutils setup...
#
import mxSetup
mxSetup.run_setup(configurations)
