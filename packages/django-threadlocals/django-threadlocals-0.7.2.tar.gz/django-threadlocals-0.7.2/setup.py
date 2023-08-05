#!/usr/bin/env python
# User: Troy Evans
# Date: 1/24/13
# Time: 8:54 PM
#
# Copyright 2015, Nutrislice Inc.  All rights reserved.
from distutils.core import setup
import threadlocals


def read_files(*filenames):
    """
    Output the contents of one or more files to a single concatenated string.
    """
    output = []
    for filename in filenames:
        f = open(filename)
        try:
            output.append(f.read())
        finally:
            f.close()
    return '\n\n'.join(output)


setup(
    name='django-threadlocals',
    packages=[
        'threadlocals',
    ],
    package_data={'threadlocals': ['license.txt', 'README.md']},
    version=threadlocals.VERSION,
    url='https://github.com/nebstrebor/django-threadlocals',
    description='Contains utils for storing and retreiving values from threadlocals, and middleware for placing the current Django request in threadlocal storage.',
    long_description=read_files('README.md'),
    author='Ben Roberts',
    author_email='ben@nutrislice.com',
    platforms=['any'],
    download_url='https://github.com/nebstrebor/django-threadlocals/tarball/%s' % threadlocals.VERSION,
    keywords=['django', 'threadlocals', 'request', 'storage'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
