#!/usr/bin/env python

""" Distutils Setup File for mxODBC.

"""
#
# Run web installer, if needed
#
import mxSetup, os
mxSetup.run_web_installer(
    os.path.dirname(os.path.abspath(__file__)),
    landmarks=('mx', 'PREBUILT'))

#
# Load configuration(s)
#
import egenix_mxodbc
configurations = (egenix_mxodbc,)

#
# Run distutils setup...
#
import mxSetup
mxSetup.run_setup(configurations)
