#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from setuptools import setup, find_packages


PYPI_RST_FILTERS = (
    # Replace code-blocks
    (r'\.\.\s? code-block::\s*(\w|\+)+', '::'),
    # Remove all badges
    (r'\.\. image:: .*', ''),
    (r'    :target: .*', ''),
    (r'    :alt: .*', ''),
)


def rst(filename):
    '''
    Load rst file and sanitize it for PyPI.
    Remove unsupported github tags:
     - code-block directive
     - all badges
    '''
    content = open(filename).read()
    for regex, replacement in PYPI_RST_FILTERS:
        content = re.sub(regex, replacement, content)
    return content


long_description = '\n'.join((
    rst('README.rst'),
    rst('CHANGELOG.rst'),
    ''
))

s3_require = ['boto']
swift_require = ['python-swiftclient']
gridfs_require = ['pymongo']
all_require = s3_require + swift_require + gridfs_require
tests_require = ['nose', 'rednose', 'mock', 'flask-mongoengine', 'pillow'] + all_require

setup(
    name='flask-fs',
    version=__import__('flask_fs').__version__,
    description=__import__('flask_fs').__description__,
    long_description=long_description,
    url='https://github.com/noirbizarre/flask-fs',
    download_url='http://pypi.python.org/pypi/flask-fs',
    author='Axel Haustant',
    author_email='noirbizarre@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['flask', 'six'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        's3': s3_require,
        'swift': swift_require,
        'gridfs': gridfs_require,
        'all': all_require,
    },
    license='MIT',
    use_2to3=True,
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)
