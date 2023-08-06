# -*- coding: utf-8 -*-
"""
weppy-Haml
----------

This extension make it possible to use a
`haml <http://haml-lang.com/>`_ syntax in weppy templates.
"""

from setuptools import setup

setup(
    name='weppy-Haml',
    version='0.2',
    url='https://github.com/gi0baro/weppy-haml',
    license='BSD',
    author='Giovanni Barillari',
    author_email='gi0baro@d4net.org',
    description='Haml syntax for weppy templates',
    long_description=__doc__,
    packages=['weppy_haml'],
    install_requires=['weppy'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
)
