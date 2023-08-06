#!/usr/bin/env python
"""
    Jean-Lou Dupont's DBus scripts
    
    Created on 2015-02-28
    @author: jldupont
"""
__author__  ="Jean-Lou Dupont"
__version__ ="0.2"

DESC="""
Overview
--------

Collection of DBus related scripts

* jlddbus-signal:  listen for a JSON object on STDIN and emit a DBus signal
"""


from distutils.core import setup
from setuptools import find_packages


setup(name=         'jlddbus',
      version=      __version__,
      description=  'Collection of DBus related tools',
      author=       __author__,
      author_email= 'jl@jldupont.com',
      #url=          'http://www.systemical.com/doc/opensource/jldzeromq',
      package_dir=  {'': "src",},
      packages=     find_packages("src"),
      scripts=      ['src/scripts/jlddbus-signal',
                     ],
      zip_safe=False
      ,long_description=DESC
      ,install_requires=[ "argparse",
                         ]
      )

#############################################

f=open("latest", "w")
f.write(str(__version__)+"\n")
f.close()

