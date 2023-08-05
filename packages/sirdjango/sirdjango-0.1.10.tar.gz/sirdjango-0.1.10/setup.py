#!/usr/bin/env python
"""
Install sirdjango using setuptools
"""

from sirdjango import __version__

with open('README.rst', 'r') as f:
    readme = f.read()

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='sirdjango',
    version=__version__,
    description='Sir Trevor integration with Django',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@takeflight.com.au',
    url='https://bitbucket.org/takeflight/sirdjango',

    install_requires=[
        'django>=1.6',
        'django-jsonfield',
        'markdown',
    ],
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
