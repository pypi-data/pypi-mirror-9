import os

import yaml

import ownrepo
import ownrepo.db


class BaseUpgrader:
    """ Base class for all the upgraders """
    original = None
    result = None

    def execute_upgrade(self, storage):
        """ Execute an upgrade """
        result = self.upgrade(storage)
        with open(os.path.join(storage, '.ownrepo', 'version'), 'w') as f:
            f.write(self.result)

    def upgrade(self, storage):
        raise NotImplementedError


class Upgrade1to2(BaseUpgrader):
    """ Upgrade from version 1 to version 2 """
    original = "1"
    result = "2"

    def upgrade(self, storage):
        db = ownrepo.db.Connection(os.path.join(storage, '.ownrepo',
                                                'ownrepo.db'))

        # Create the new settings table
        db.query('CREATE TABLE settings ('
                 '    key TEXT PRIMARY KEY UNIQUE NOT NULL,'
                 '    value TEXT,'
                 '    is_system INTEGER'
                 ');', edit=True)

        # Move all the settings to the database
        with open(os.path.join(storage, '.ownrepo', 'settings.yml')) as f:
            old_settings = yaml.load(f.read())
        system_keys = 'brand', 'password_salt'
        for key, value in old_settings.items():
            is_system = key in system_keys
            db.query('INSERT INTO settings (key, value, is_system) VALUES '
                     '(?, ?, ?)', key, value, is_system, edit=True)

        # Remove the old settings file
        os.remove(os.path.join(storage, '.ownrepo', 'settings.yml'))

        db.close()

        # Rename the database from ownrepo.db to database
        old = os.path.join(storage, '.ownrepo', 'ownrepo.db')
        new = os.path.join(storage, '.ownrepo', 'database')
        os.rename(old, new)


def get_upgraders():
    """ Get a list of upgraders registered in this module """
    upgraders = []
    upgraders.append(Upgrade1to2())
    return upgraders


def get_upgrade_path(current, latest=None, upgraders=None, *, _result=None):
    """ Get the fastest upgrade path to the newest version """
    upgraders = upgraders if upgraders is not None else get_upgraders()
    result = _result if _result is not None else []
    latest = latest if latest is not None else ownrepo.storage_version

    # If the current release is the same as the latest return
    if current == latest:
        return result

    # Get all upgraders which starts from this version
    from_which = [upgrader for upgrader in upgraders
                  if upgrader.original == current]

    if not from_which:
        raise RuntimeError('Can\'t find an upgrade path')

    # Add to the result the one which upgrade to the greatest version
    result.append(sorted(from_which, key=lambda v: v.result)[-1])

    # Call the function in recursive mode
    return get_upgrade_path(result[-1].result, latest, upgraders,
                            _result=result)
