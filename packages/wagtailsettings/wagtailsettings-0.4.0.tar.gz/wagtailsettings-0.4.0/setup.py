#!/usr/bin/env python
"""
Install wagtailsettings using setuptools
"""

from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme = f.read()

with open('wagtailsettings/version.py') as v:
    version = '0.0.0'
    exec(v.read())  # Get version


setup(
    name='wagtailsettings',
    version=version,
    description='Admin-editable settings for Wagtail projects',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@takeflight.com.au',
    url='https://bitbucket.org/takeflight/wagtailsettings',

    install_requires=['wagtail>=0.9'],
    zip_safe=False,
    license='BSD License',

    packages=find_packages(),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
