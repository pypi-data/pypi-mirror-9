#!/usr/bin/env python
"""
Install sirdjango_takeflight using setuptools
"""

from sirdjango_takeflight import __version__

with open('README.rst', 'r') as f:
    readme = f.read()

from setuptools import setup, find_packages

setup(
    name='sirdjango_takeflight',
    version=__version__,
    description=('Reusable Sir Trevor blocks'),
    long_description=readme,
    author='Takeflight',
    author_email='admin@takeflight.com.au',
    url='https://bitbucket.org/takeflight/sirdjango_takeflight/',

    install_requires=[
        'sirdjango',
    ],
    zip_safe=False,
    license='BSD License',

    packages=find_packages(),

    include_package_data=True,
    package_data={ },

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
