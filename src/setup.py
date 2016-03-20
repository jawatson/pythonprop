#!/usr/bin/env python


"""
This script is used to install core utils in a virtual environmnt.
"""

from distutils.core import setup

setup(name='pythonprop',
      version='0.1',
      description='VOA Propagation Prediction Plotting Utilities',
      author='James Watson',
      author_email='jwatson@mac.com',
      py_modules=['pythonprop.hamlocation',
                    'pythonprop.voaAreaRect'],
     )
