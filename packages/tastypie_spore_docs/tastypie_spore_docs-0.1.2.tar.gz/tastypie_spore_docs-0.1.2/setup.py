#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'mnowotka'

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='tastypie_spore_docs',
    version='0.1.2',
    author='Michal Nowotka',
    author_email='mnowotka@ebi.ac.uk',
    description='This Django app generates SPORE endpoint from Tastypie REST API and provides a JavaScript based SPORE client.',
    url='https://www.ebi.ac.uk/chembldb/index.php/ws',
    license='Apache Software License',
    packages=['tastypie_spore_docs'],
    long_description=open('README.rst').read(),
    install_requires=[
        'django-tastypie',
    ],
    include_package_data=True,
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Software Development :: Documentation'],
    zip_safe=False,
)
