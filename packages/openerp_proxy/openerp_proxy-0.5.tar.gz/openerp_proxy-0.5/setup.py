#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import openerp_proxy.version

setup(name='openerp_proxy',
      version=openerp_proxy.version.version,
      description='Odoo/OpenERP CLI interface and library for RPC',
      author='Dmytro Katyukha',
      author_email='firemage.dima@gmail.com',
      url='https://github.com/katyukha/openerp-proxy',
      long_description=open('README.rst').read(),
      packages=['openerp_proxy',
                'openerp_proxy.connection',
                'openerp_proxy.service',
                'openerp_proxy.orm',
                'openerp_proxy.ext',
                'openerp_proxy.plugins'],
      scripts=['bin/openerp_proxy'],
      license="GPL",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries',
      ],
      keywords=['openerp', 'odoo', 'rpc', 'xmlrpc', 'xml-rpc', 'json-rpc', 'jsonrpc'],
      extras_require={
          'ipython_shell': ['ipython'],
      },
      install_requires=[
          'extend_me>=1.1.1',
      ],
)
