#!/usr/bin/env python
"""
    Jean-Lou Dupont's Raspberry Pi scripts
    
    Created on 2015-03-08
    @author: jldupont
"""
__author__  ="Jean-Lou Dupont"
__version__ ="0.3"

DESC="""
Overview
--------

Collection of Raspberry Pi related scripts

* jldrpi-input : listen for GPIO input events and output JSON result on stdout
"""


from distutils.core import setup
from setuptools import find_packages


setup(name=         'jldrpi',
      version=      __version__,
      description=  'Collection of Raspberry Pi related tools',
      author=       __author__,
      author_email= 'jl@jldupont.com',
      url=          'https://github.com/jldupont/jldrpi',
      package_dir=  {'': "src",},
      packages=     find_packages("src"),
      scripts=      ['src/scripts/jldrpi-input',
                     ],
      zip_safe=False
      ,long_description=DESC
      ,install_requires=[ "argparse", "RPi.GPIO"
                         ]
      )

#############################################

f=open("latest", "w")
f.write(str(__version__)+"\n")
f.close()

