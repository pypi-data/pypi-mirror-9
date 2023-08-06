#!python3
import os

import hashlib
import yaml
import pkg_resources
import flask
import werkzeug


class RepositoriesManager:
    """ Manage all repositories """

    def __init__(self, app):
        self._app = app
        self._db = self._app.ownrepo_db

    def list(self):
        """ Return a list of accessible repositories """
        repos = self._db().query('SELECT * FROM repos')
        acls = self._db().query('SELECT * FROM acls')
        inheritances = self._db().query('SELECT * FROM inheritances')

        result = {}
        for data in repos:
            acl = [acl for acl in acls if acl['repo'] == data['name']]
            repo = Repository(self, data, acl)
            if repo.readable:
                result[repo.name] = repo

        # Register also inheritances
        for inheritance in inheritances:
            try:
                from_ = result[inheritance['inherit_from']]
                to = result[inheritance['inherit_to']]
            except KeyError:
                pass
            else:
                to.add_inheritance(from_, inheritance['weight'])

        return result

    def get(self, name):
        """ Return an accessible repository """
        data = self._db().query('SELECT * FROM repos WHERE name = ?', name,
                                one=True)
        if data:
            acls = self._db().query('SELECT * FROM acls WHERE repo = ?', name)
            repo = Repository(self, data, acls)
            if repo.readable:
                # Register inheritances
                inheritances = self._db().query('SELECT * FROM inheritances '
                                                'WHERE inherit_to = ?',
                                                repo.name)
                for inheritance in inheritances:
                    try:
                        inherit_from = self.get(inheritance['inherit_from'])
                    except ValueError:
                        pass
                    else:
                        repo.add_inheritance(inherit_from,
                                             inheritance['weight'])

                return repo
            raise ValueError('Not enough privileges for reading {}'
                             .format(name))
        else:
            raise ValueError('Invalid repository: {}'.format(name))

    def exists(self, name):
        """ Check if a repository exists """
        exists = self._db().query('SELECT * FROM repos WHERE name = ?', name,
                                  one=True)
        return bool(exists)


class Repository:
    """ Representation of a repository """

    def __init__(self, manager, data, acls):
        self._manager = manager
        self._db = manager._db
        self._data = data
        self._acls = acls
        self._directory = os.path.join(flask.current_app.ownrepo_storage,
                                       data['name'])

        self._read_acls = [acl['user'] for acl in acls
                           if acl['allow_to'] == 'read']
        self._write_acls = [acl['user'] for acl in acls
                            if acl['allow_to'] == 'write']

        self.name = data['name']
        self.public = bool(data['is_public'])
        self.private = not self.public

        self.inheritances = []
        self.weighted_inheritances = {}
        self.inherited_packages = {}

        self._load_packages()

    def __str__(self):
        return self.name

    def _load_packages(self):
        """ Load all packages in this repository """
        data = self._db().query('SELECT * FROM releases WHERE repo = ?',
                                self.name)

        # Build the packages dict
        packages = {}
        for one in data:
            if one['package'] not in packages:
                packages[one['package']] = Package(self, one['package'])
            packages[one['package']].register_release(one)
        self.packages = packages

        self._recalculate_all_packages()

    def _recalculate_inheritances(self):
        """ Recalculate inheritances order """
        self.inheritances = []
        for weight in reversed(sorted(self.weighted_inheritances.keys())):
            self.inheritances += self.weighted_inheritances[weight]

        self._recalculate_all_packages()

    def _recalculate_all_packages(self):
        """ Merge inherited and this repository's packages """
        self.inherited_packages = {}
        for repo in reversed(self.inheritances):
            self.inherited_packages.update(repo.packages)

        self.all_packages = self.inherited_packages
        self.all_packages.update(self.packages)

    @property
    def url(self):
        return flask.url_for('web.simple_repo', repo=self.name,
                             _external=True)

    @property
    def readable(self):
        # If all can read the repository return True
        if self.public:
            return True

        # If the user isn't authenticated return False
        if getattr(flask.g, 'authenticated_as', None) is None:
            return False

        # If the user isn't allowed return False
        if flask.g.authenticated_as not in self._read_acls:
            return False

        return True

    @property
    def writable(self):
        # If the user isn't authenticated return False
        if getattr(flask.g, 'authenticated_as', None) is None:
            return False

        # If the user isn't allowed return False
        if flask.g.authenticated_as not in self._write_acls:
            return False

        return True

    def add_inheritance(self, repo, weight):
        """ Add an inheritance from one repo """
        if repo in self.inheritances:
            return
        self.inheritances.append(repo)

        if weight not in self.weighted_inheritances:
            self.weighted_inheritances[weight] = []
        self.weighted_inheritances[weight].append(repo)

        self._recalculate_inheritances()

    def packages_via_inheritance(self, inheritance):
        """ Get packages available via that inheritance """
        return {name: package for name, package in
                inheritance.packages.items() if name not in self.packages and
                self.inherited_packages[name].repo == inheritance}

    def create_package(self, name):
        """ Create a new package on the repository """
        name = name.lower()  # Name must be lower case

        if name in self.packages:
            raise NameError('Package already exists')

        # Load the new package
        self.packages[name] = Package(self, name)


class Package:
    """ Representation of a package """

    def __init__(self, repo, name):
        self.repo = repo
        self.name = name.lower()
        self.releases = {}
        self._db = repo._db

        self._calculate_releases()

    def __str__(self):
        return self.name

    def _calculate_releases(self):
        """ Calculate available releases """
        sort_releases = lambda r: pkg_resources.parse_version(r)
        self.releases_sorted = list(reversed(sorted(self.releases.keys(),
                                                    key=sort_releases)))

    def register_release(self, data):
        """ Add a release to the package """
        if data['version'] not in self.releases:
            self.releases[data['version']] = []
        self.releases[data['version']].append(data['file'])
        self._calculate_releases()

    def files(self, release=None):
        """ Get all available files """
        # Calculate md5 of a file
        md5 = lambda f: hashlib.md5(open(self.repo._directory+'/'+f, 'rb')
                                    .read()).hexdigest()

        # Capture all files of this package or release if it's passed
        releases = self.releases
        if release:
            releases = {release: self.releases[release]}
        files = {}
        for name, release in releases.items():
            for one in release:
                files[one] = md5(one)
        return files

    def add_release(self, version, archive_type, archive, md5=None):
        """ Add a new release to the package """
        # Save the new archive
        file_name = werkzeug.secure_filename(archive.filename)
        archive.save(self.repo._directory+'/'+file_name)

        self._db().query('INSERT INTO releases (repo, package, file, version,'
                         ' type) VALUES (?, ?, ?, ?, ?)', self.repo.name,
                         self.name, file_name, version, archive_type,
                         edit=True)

        # Update cache
        self.register_release({'repo': self.repo.name, 'package': self.name,
                               'file': file_name, 'version': version,
                               'type': archive_type})

    def install_command(self, release=None):
        """ Generate the command for installing this package """
        parts = ['pip install '+self.name]
        if release:
            parts.append('=='+release)
        parts.append(' -i '+self.repo.url)
        return "".join(parts)
