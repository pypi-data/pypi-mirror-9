
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


