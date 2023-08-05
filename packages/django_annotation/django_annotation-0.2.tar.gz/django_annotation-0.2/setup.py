#!/usr/bin/env python
import os, sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit(0)

with open('README.rst') as f:
    long_description = f.read()

# Dynamically calculate the version based on swingtime.VERSION.
VERSION = __import__('annotation').__version__

setup(
    name='django_annotation',
    version=VERSION,
    url='https://github.com/dakrauth/django-annotation',
    author_email='dakrauth@gmail.com',
    description='Basic content management.',
    long_description=long_description,
    author='David A Krauth',
    platforms=['any'],
    license='MIT License',
    classifiers=(
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    packages=['annotation'],
    install_requires=['markdown2', 'django>=1.5', 'choice_enum']
)
