#!/usr/bin/env python
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='django-localflavor-au-tjh',
    version='1.1.2',
    description='Country-specific Django helpers for Australia.',
    long_description=README,
    author='Django Software Foundation',
    author_email='webmaster@ionata.com.au',
    license='BSD',
    url='https://bitbucket.org/tim_heap/django-localflavor-au',
    packages=['django_localflavor_au'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'Django>=1.4',
    ]
)
