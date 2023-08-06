# -*- coding: utf-8 -*-
'''
@author: saaj
'''


import sys

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

  
# See ``qxcpjsonrpc.test`` docstring for the purpose 
sys.warnoptions.append('always')  


setup(
  name             = 'QooxdooCherrypyJsonRpc',
  version          = '0.5.1',
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  packages         = ['qxcpjsonrpc', 'qxcpjsonrpc.test'],
  package_data     = {'qxcpjsonrpc.test' : ['fixture/*']},    
  test_suite       = 'qxcpjsonrpc.test.suite',
  url              = 'https://bitbucket.org/saaj/qooxdoo-cherrypy-json-rpc',
  license          = 'LGPL-2.1+',
  description      = 'Qooxdoo-specific CherryPy-based JSON RPC-server',
  long_description = open('README.txt').read(),
  install_requires = ['CherryPy >= 3.2'],
  platforms        = ['Any'],
  keywords         = 'qooxdoo cherrypy javascript python rpc',
  classifiers      = [
    'Topic :: Communications',
    'Topic :: Software Development :: Libraries',
    'Framework :: CherryPy',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Intended Audience :: Developers'
  ]
)

