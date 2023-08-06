#!/usr/bin/env python

from distutils.core import setup
import py2exe
from nsis import build_installer


setup(name='PySimpleSOAP',
      version='1.03d',
      description='Python Simple SOAP Library',
      author='Mariano Reingart',
      author_email='reingart@gmail.com',
      url='http://code.google.com/p/pysimplesoap',
      console=['client.py'],
      cmdclass = {"py2exe": build_installer},
     )

