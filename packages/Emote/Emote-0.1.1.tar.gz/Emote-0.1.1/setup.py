#!/usr/bin/env python


"""
Setup script for emote
"""


import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as f:
    readme_content = f.read().strip()


with open('LICENSE.txt') as f:
    license_content = f.read().strip()


version = None
author = None
email = None
source = None
with open(os.path.join('emote', '__init__.py')) as f:
    for line in f:
        if line.strip().startswith('__version__'):
            version = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__author__'):
            author = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__email__'):
            email = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__source__'):
            source = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif None not in (version, author, email, source):
            break

setup(
    name='Emote',
    author=author,
    author_email=email,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Utilities'
    ],
    description="Simple emoji lookups for Python.",
    include_package_data=True,
    license=license_content,
    long_description=readme_content,
    packages=['emote'],
    url=source,
    version=version,
    zip_safe=True,
)
