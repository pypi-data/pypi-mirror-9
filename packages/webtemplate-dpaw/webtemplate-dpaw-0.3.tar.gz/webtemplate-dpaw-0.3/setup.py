#!/usr/bin/env python

from setuptools import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

install_requires = [
    'Django>=1.6',
]
version = ('0.3')

setup(
    name='webtemplate-dpaw',
    version=version,
    install_requires=install_requires,
    tests_require=install_requires,
    test_suite='runtests.runtests',
    packages=['webtemplate_dpaw'],
    include_package_data=True,
    author='Ashley Felton',
    author_email='asi@dpaw.wa.gov.au',
    maintainer='Ashley Felton',
    maintainer_email='asi@dpaw.wa.gov.au',
    license='Apache License, Version 2.0',
    url='https://bitbucket.org/dpaw/webtemplate-dpaw',
    description='Base HTML templates for DPaW Django projects',
    long_description=README,
    keywords=['django', 'html', 'template', 'dpaw'],
    classifiers=[
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
