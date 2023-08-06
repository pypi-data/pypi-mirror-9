#!/usr/bin/env python

from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md').read()

setup(
    name='wooper',
    version="0.4.0",
    description="FrisbyJS-inspired REST API testing helpers and steps \
for 'behave' behavior-driven development testing library",
    long_description=LONG_DESCRIPTION,
    author='Yauhen Kirylau',
    author_email='actionless.loveless@gmail.com',
    url='http://github.com/actionless/wooper',
    license=open('LICENSE').read(),
    platforms=["any"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests==2.3.0',
        'behave==1.2.5a1'
    ],
    dependency_links=[
        "https://github.com/actionless/behave/zipball/master#egg=behave-1.2.5a1",
    ],
    classifiers=[
        # @TODO: change status
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        # @TODO: add testers
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        # @TODO: add version
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)
