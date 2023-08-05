#!python3
import os

import yaml
import click

import ownrepo


class ConfigFile(dict):
    """
    Class to manage a configuration file
    """

    def __init__(self, storage, file_name):
        self._path = os.path.join(storage, '.ownrepo', file_name+'.yml')
        self.read()  # Read the config one time

    def read(self):
        """ Read the configuration and update the config """
        try:
            with open(self._path, 'r') as f:
                config = yaml.load(f.read())
        except OSError:
            click.echo("Error: unable to read the configuration file: {}"
                       .format(self._path), err=True)
            exit(1)
        except yaml.YAMLError as e:
            click.echo("Error: Syntax error in the configuration file:",
                       err=True)
            click.echo(e, err=True)
            exit(1)
        else:
            self.clear()  # First clear the dictionary

            # If the file is empty
            try:
                self.update(config)
            except TypeError:
                pass

    def save(self):
        """ Save the configuration """
        try:
            with open(self._path, 'w') as f:
                f.write(yaml.dump(dict(self.items()),
                                  default_flow_style=False))
        except OSError:
            click.echo("Error: unable to write the configuration file to {}"
                       .format(self._path), err=True)
            exit(1)


def check_storage(path):
    """ Return if a storage path is an ownrepo storage directory """
    # The directory must exists
    if not os.path.exists(path):
        return False, "storage directory doesn't exist"

    # It must have a .ownrepo subdirectory
    subdir = os.path.join(path, '.ownrepo')
    if not os.path.exists(subdir) or not os.path.isdir(subdir):
        return False, "storage directory isn't an OwnRepo storage directory"

    # It must be for the correct version
    if not os.path.exists(os.path.join(subdir, 'version')):
        return False, "storage directory hasn't the version file"
    with open(os.path.join(subdir, 'version'), 'r') as f:
        version = f.read()
    if version.strip() != ownrepo.storage_version:
        return False, "storage directory is for another release of OwnRepo"

    # It must have some files in the .ownrepo subdirectory
    needed_files = ('settings.yml', 'ownrepo.db')
    for one in needed_files:
        if not os.path.exists(os.path.join(subdir, one)):
            return False, "the storage directory is incomplete (some files" \
                          "missing)"

    return True, ""
