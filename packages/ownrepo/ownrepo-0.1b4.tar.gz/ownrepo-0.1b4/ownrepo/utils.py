#!python3
import os

import click

import ownrepo


def check_storage(path, strict=True):
    """ Return if a storage path is an ownrepo storage directory """
    # The directory must exists
    if not os.path.exists(path):
        return False, "storage directory doesn't exist"

    # It must have a .ownrepo subdirectory
    subdir = os.path.join(path, '.ownrepo')
    if not os.path.exists(subdir) or not os.path.isdir(subdir):
        return False, "storage directory isn't an OwnRepo storage directory"

    # It must have a version file
    if not os.path.exists(os.path.join(subdir, 'version')):
        return False, "storage directory hasn't the version file"

    # Here the "soft" version ends
    if not strict:
        return True, ""

    # It must be for the current release of OwnRepo
    with open(os.path.join(subdir, 'version'), 'r') as f:
        version = f.read()
    if version.strip() != ownrepo.storage_version:
        return False, "storage directory is for another release of OwnRepo"

    # It must have some files in the .ownrepo subdirectory
    needed_files = ('database',)
    for one in needed_files:
        if not os.path.exists(os.path.join(subdir, one)):
            return False, "the storage directory is incomplete (some files " \
                          "missing)"

    return True, ""
