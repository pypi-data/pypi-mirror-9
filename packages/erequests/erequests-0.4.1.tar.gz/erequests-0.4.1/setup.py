# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name                 = 'erequests',
    version              = '0.4.1',
    url                  = 'https://github.com/saghul/erequests',
    license              = 'BSD',
    author               = 'Saúl Ibarra Corretgé',
    author_email         = 'saghul@gmail.com',
    description          = 'Requests + Eventlet',
    long_description     = open('README.rst', 'r').read(),
    install_requires     = ['eventlet', 'requests'],
    py_modules           = ['erequests'],
    zip_safe             = False,
    include_package_data = True,
    platforms            = 'any',
    classifiers          = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

