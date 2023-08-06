#!/usr/bin/python3
"""
OwnRepo
-------

OwnRepo is a Python packages repository, built with Python 3 and Flask, which
features multiple repository in a single running instance, support for public
and private repositories, users and a powerful ACL system in order to limit
access for some of your users.

Quickstart
``````````

It's really easy to set up a working OwnRepo instance::

    $ pip install ownrepo
    $ ownrepo init --sample storage_directory
    $ cd storage_directory
    $ ownrepo run

These commands will fetch and install OwnRepo from PyPI,  create a new storage
directory located at ``storage_directory/``, and from within of it run
OwnRepo.

The ``--sample`` flag will initialize the storage directory with some sample
data: two repositories, one with public access (called ``public``) and another
with restricted access (called ``private``). It will also create an user
called ``admin`` (with password ``admin``), who will have full read and write
access on both repositories.
"""


import setuptools

setuptools.setup(
    name = 'ownrepo',
    version = '0.1b5',
    url = 'http://ownrepo.pietroalbini.io/',
    author = 'Pietro Albini',
    author_email = 'pietro@pietroalbini.io',
    license = 'MIT',
    description = 'Simple, easy-to-setup private Python packages repository',
    long_description = __doc__,

    packages = [
        'ownrepo',
    ],

    entry_points = {
        'console_scripts': [
            'ownrepo = ownrepo.__main__:cli',
        ],
    },

    include_package_data = True,
    zip_safe = False,

    install_requires =  [
        'flask',
        'pyyaml',
        'setuptools',
        'click',
        'gunicorn',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Console',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Software Distribution',
    ],
)
