#!/usr/bin/python

from distutils.core import setup

setup(
    name='tll',
    version='0.1dev',
    packages=['tll'],
    author='Dimas Moreira Junior',
    author_email='dimasmjunior@gmail.com',
    description='Thin LDAP Layer',
    license='BSD',
    url='http://github.com/dimasmjunior/python-tll',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
    ],
)
