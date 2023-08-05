#!/usr/bin/env python

from setuptools import setup
import sys

install_requires = [
    'openpyxl>=2.1.4',
    'MarkupSafe>=0.21'
]

if sys.version_info < (2, 7):
    install_requires.append('ordereddict>=1.1')

setup(
    name='copytext',
    version='0.1.8',
    description='A library for accessing a spreadsheet as a native Python object suitable for templating.',
    long_description=open('README').read(),
    author='NPR Visuals Team',
    author_email='nprapps@npr.org',
    url='http://copytext.readthedocs.org/',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    py_modules=['copytext'],
    install_requires=install_requires
)
