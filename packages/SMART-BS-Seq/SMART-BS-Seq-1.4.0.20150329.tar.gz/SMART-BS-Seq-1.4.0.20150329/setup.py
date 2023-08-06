#!/usr/bin/env python
# Time-stamp: <2015-03-29 13:01:00 Hongbo Liu>

"""Description: SMART setup

Copyright (c) 2014 Hongbo Liu <hongbo919@gmail.com>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD License (see the file COPYING included
with the distribution).

@status: release candidate
@version: 1.4.0
@author:  Hongbo Liu
@contact: hongbo919@gmail.com
"""

# ------------------------------------
# python modules
# ------------------------------------
from distutils.core import setup
import sys
# Use build_ext from Cython if found
command_classes = {}

try: 
    from scipy import get_include as scipy_get_include 
    scipy_include_dir = [scipy_get_include()] 
except: 
    scipy_include_dir = []
    sys.stderr.write("CRITICAL:Scipy must be installed!\n")
    sys.exit(1)

def main():
    if float(sys.version[:3])<2.7 or float(sys.version[:3])>=2.8:
        sys.stderr.write("CRITICAL: Python version must be 2.7!\n")
        sys.exit(1)
    
    setup(name="SMART-BS-Seq",
          version="1.4.0.20150329",
          description="Specific Methylation Analysis and Report Tool for BS-Seq data",
          long_description=open('README.rst', 'rt').read(),
          author='Hongbo Liu',
          author_email='hongbo919@gmail.com',
          url='http://methymark.edbc.org/SMART/',
          package_dir={'SMART' : 'SMART'},
          packages=['SMART'],
          package_data={'SMART':['Example/BSSeq_fortest/*.wig.gz','Example/CLoc_hg19_fortest/*.txt.gz']},
          #py_modules = ['Splitchrome','MethyMergeEntropy','SegmentationNormal','Folderprocess','NewEntropy','NewEntropyNormal'],    
          scripts=['bin/SMART'],
          classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Environment :: Web Environment',
              'Intended Audience :: End Users/Desktop',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: Python Software Foundation License',
              'Operating System :: POSIX :: Linux',
              'Operating System :: Microsoft :: Windows',
              'Programming Language :: Python',
              ],
          cmdclass = command_classes
          #install_requires=['scipy>=0.13',
                            #],
          )


if __name__ == '__main__':
    main()