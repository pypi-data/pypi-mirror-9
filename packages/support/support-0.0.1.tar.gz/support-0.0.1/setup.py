# -*- coding: utf-8 -*-

"""
    support
    ~~~~~~~

    An evented server framework designed for building scalable
    and introspectable services. Built at PayPal, based on gevent.

    :copyright: (c) 2015 by Mahmoud Hashemi, Kurt Rose, Mark Williams, and Chris Lane
    :license: BSD, see LICENSE for more details.

"""

import sys
from setuptools import setup


__author__ = 'Mahmoud Hashemi, Kurt Rose, Mark Williams, and Chris Lane'
__version__ = '0.0.1'
__contact__ = 'mahmoud@paypal.com'
__url__ = 'https://github.com/paypal/support'
__license__ = 'BSD'

desc = ('An evented server framework designed for building scalable'
        ' and introspectable services. Built at PayPal, based on gevent.')

if sys.version_info[:2] != (2, 7):
    raise NotImplementedError("Sorry, SuPPort only supports Python 2.7")


if __name__ == '__main__':
    setup(name='support',
          version=__version__,
          description=desc,
          long_description=__doc__,
          author=__author__,
          author_email=__contact__,
          url=__url__,
          packages=['support',
                    'support.meta_service'],
          include_package_data=True,
          zip_safe=False,
          install_requires=['boltons==0.4.1',
                            'cffi==0.8.6',
                            'clastic==0.4.2',
                            'cryptography==0.7.2',
                            'enum34==1.0.4',
                            'faststat==0.3.1',
                            'gevent==1.0.1',
                            'greenlet==0.4.5',
                            'hyperloglog==0.0.9',
                            'lithoxyl>=0.1.0',
                            'psutil==2.2.1',
                            'py==1.4.26',
                            'pyasn1==0.1.7',
                            'pycparser==2.10',
                            'pyjks>=0.3.0.1',
                            'pyOpenSSL==0.14',
                            'pytest==2.6.4',
                            'sampro==0.1',
                            'ufork>=0.0.1',
                            'six==1.9.0',
                            'Werkzeug==0.9.4'],
          license=__license__,
          platforms='any',
          classifiers=[
              'Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
              'Topic :: Internet :: WWW/HTTP :: WSGI',
              'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
              'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
              'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
              'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
              'Topic :: Software Development :: Libraries :: Application Frameworks',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: Implementation :: CPython',
              'License :: OSI Approved :: BSD License'])
