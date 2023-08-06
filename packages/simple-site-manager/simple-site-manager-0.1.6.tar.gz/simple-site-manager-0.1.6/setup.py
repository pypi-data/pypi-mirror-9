# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='simple-site-manager',

    version='0.1.6',

    description='Manage multiple lighttpd and Django or Flask websites on a single machine. ',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/zeraien/simple-site-manager',

    # Author details
    author='Dmitri Fedortchenko',
    author_email='info@onedaybeard.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='lighttpd fcgi tool management',
    packages=['simple_site_manager'],
    install_requires=['jinja2', 'pyyaml'],

    package_data={
        'simple_site_manager': ['templates/*.jinja2'],
    },
    entry_points={
        'console_scripts': [
            'siteman = simple_site_manager:main_func',
        ],
    }
)
