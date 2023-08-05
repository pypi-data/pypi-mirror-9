#!python3
import os
import getpass
import hashlib
import distutils.util
import shutil

import click
import pkg_resources

import ownrepo
import ownrepo.authentication
import ownrepo.db
from ownrepo.utils import check_storage, ConfigFile


def error(message, *replace):
    """ Print an error message and exit """
    click.echo('Error: '+message.format(*replace), err=True)
    exit(1)


@click.group()
@click.option('--storage', '-s', help='The storage directory', default='.')
@click.pass_context
def cli(ctx, storage):
    """ Manage your OwnRepo instance """
    # Detect the configuration path
    if storage:
        storage_path = storage
    elif 'OWNREPO_STORAGE' in os.environ:
        storage_path = os.environ['OWNREPO_STORAGE']
    else:
        error("unable to locate the storage directory")

    # Don't check storage validity for these commands
    not_check_storage = ['init']

    if ctx.invoked_subcommand not in not_check_storage:
        if not check_storage(storage_path):
            error("invalid storage directory: {}",
                  os.path.realpath(storage_path))

        ctx.obj = {}
        ctx.obj['storage'] = os.path.realpath(storage_path)

    else:
        ctx.obj = {}
        ctx.obj['storage'] = None

    # If a storage path was provided init the database and settings file
    if ctx.obj['storage']:
        db_path = os.path.join(ctx.obj['storage'], '.ownrepo', 'ownrepo.db')
        ctx.obj['db'] = ownrepo.db.Connection(db_path)
        ctx.obj['settings'] = ConfigFile(ctx.obj['storage'], 'settings')


@cli.command()
@click.option('-b', '--bind', help='The IP to bind the port',
              default='0.0.0.0')
@click.option('-p', '--port', help='The port to listen on', default=80)
@click.option('-w', '--workers', help='How much workers run', default=3)
@click.option('-d', '--debug', help='Run in debug mode', is_flag=True)
@click.pass_context
def run(ctx, bind, port, debug, workers):
    """ Run the webserver """
    # If the application is in debug mode run it with the flask's own server
    if debug:
        app = ownrepo.create_app(ctx.obj['storage'])
        app.run(host=bind, port=port, debug=debug)
    # Else run the application with gunicorn
    else:
        options = {
            'bind': bind+':'+str(port),
            'workers': workers,
            'accesslog': '-',  # Standard output
            'errorlog': '-',  # Standard error
        }
        app = ownrepo.create_gunicorn_process(ctx.obj['storage'], options)

        try:
            app.run()  # Run gunicorn, not flask!
        except SystemExit:
            pass


@cli.command('add-user')
@click.argument('name')
@click.option('--password', '-p', help='The user\'s password', default='')
@click.pass_context
def add_user(ctx, name, password):
    """ Add an user """
    db = ctx.obj['db']
    users = db.query('SELECT DISTINCT name FROM USERS')

    # Check if the user already exists
    if name in users:
        error('the user {} already exists', name)

    # Ask the password only if it wasn't provided before
    if password == '':
        password = getpass.getpass()

    # Hash the password (salted sha512) and add the user
    hashed = ownrepo.authentication.hash_password(ctx.obj['settings'], name,
                                                  password)
    db.query('INSERT INTO users (name, password) VALUES (?, ?)', name, hashed,
             edit=True)


@cli.command('remove-user')
@click.argument('name')
@click.option('-y', '--yes', help='Skip confirmation', is_flag=True)
@click.pass_context
def remove_user(ctx, name, yes):
    """ Remove an user """
    db = ctx.obj['db']

    # Check if the user doesn't exist
    exists = db.query('SELECT name FROM users WHERE name = ?', name, one=True)
    if not exists:
        error('the user {} doesn\'t exist', name)

    if not yes:
        click.echo('Are you sure you want to delete user {}? [y/N] '
                   .format(name), nl=False)
        response = click.getchar()
        click.echo()
        try:
            if not distutils.util.strtobool(response):
                raise ValueError  # Skip to the exception block
        except ValueError:
            exit(0)

    # Delete the user
    db.query('DELETE FROM users WHERE name = ?', name, edit=True)
    db.query('DELETE FROM acls WHERE user = ?', name, edit=True)


@cli.command('change-password')
@click.argument('name')
@click.option('--password', '-p', help='The new password', default='')
@click.pass_context
def change_password(ctx, name, password):
    """ Change an user's password """
    db = ctx.obj['db']
    settings = ctx.obj['settings']

    # Check if the user doesn't exist
    exists = db.query('SELECT * FROM users WHERE name = ?', name, one=True)
    if not exists:
        error('the user {} doesn\'t exists', name)

    # Ask for the new password only if it wasn't provided before
    if password == '':
        password = getpass.getpass()

    # Hash the password (salted sha512) and add the user
    hashed = ownrepo.authentication.hash_password(settings, name, password)
    db.query('UPDATE users SET password = ? WHERE name = ?', hashed, name,
             edit=True)


@cli.command('add-repo')
@click.argument('name')
@click.option('--public', help='Mark the repo as public', is_flag=True)
@click.option('--allow-read', help='Allow this user to view the repo',
              multiple=True)
@click.option('--allow-write', help='Allow this user to upload to the repo',
              multiple=True)
@click.pass_context
def add_repo(ctx, name, public, allow_read, allow_write):
    """ Add a new repository """
    db = ctx.obj['db']
    settings = ctx.obj['settings']

    # Check if the repository already exists
    exists = db.query('SELECT * FROM repos WHERE name = ?', name, one=True)
    if exists:
        error('repository {} already exists', name)

    # Create the repository in the db
    db.query('INSERT INTO repos (name, is_public) VALUES (?, ?)', name,
             int(public), edit=True)

    # Create the repo directory
    os.makedirs(os.path.join(ctx.obj['storage'], name))

    users = [user['name'] for user in
             db.query('SELECT DISTINCT name FROM users')]
    for thing, who in {'read': allow_read, 'write': allow_write}.items():
        for user in who:
            if user not in users:
                error('user {} doesn\'t exist', user)
            db.query('INSERT INTO acls (repo, user, allow_to) VALUES '
                     '(?, ?, ?)', name, user, thing, edit=True)


@cli.command('remove-repo')
@click.argument('name')
@click.option('-y', '--yes', help='Skip confirmation', is_flag=True)
@click.pass_context
def remove_repo(ctx, name, yes):
    """ Remove a repository """
    db = ctx.obj['db']

    # Check if the repository doesn't exist
    exists = db.query('SELECT * FROM repos WHERE name = ?', name, one=True)
    if not exists:
        error('the repo {} doesn\'t exist', name)

    if not yes:
        click.echo('Are you sure you want to delete repo {}? [y/N] '
                   .format(name), nl=False)
        response = click.getchar()
        click.echo()
        try:
            if not distutils.util.strtobool(response):
                raise ValueError  # Skip to the exception block
        except ValueError:
            exit(0)

    # If FileNotFoundError is raised, there is less work to do \o/
    try:
        shutil.rmtree(ctx.obj['storage']+'/'+name)
    except FileNotFoundError:
        pass

    db.query('DELETE FROM acls WHERE repo = ?', name, edit=True)
    db.query('DELETE FROM repos WHERE name = ?', name, edit=True)


@cli.command('acl')
@click.argument('repo')
@click.option('--allow-read', help='Allow this user to view the repo',
              multiple=True)
@click.option('--allow-write', help='Allow this user to upload to the repo',
              multiple=True)
@click.option('--deny-read', help='Deny this user to view the repo',
              multiple=True)
@click.option('--deny-write', help='Deny this user to upload to the repo',
              multiple=True)
@click.option('--public', help='Convert the repo to public', is_flag=True)
@click.option('--private', help='Convert the repo to private', is_flag=True)
@click.pass_context
def acl(ctx, repo, allow_read, allow_write, deny_read, deny_write, public,
        private):
    """ Update a repo's acl """
    db = ctx.obj['db']

    # Check if the repository exists
    exists = db.query('SELECT * FROM repos WHERE name = ?', repo, one=True)
    if not exists:
        error('repository {} doesn\'t exist', repo)

    # Update the visibility status
    if public or private:
        is_public = 1 if public else 0
        db.query('UPDATE repos SET is_public = ? WHERE name = ?',
                 int(is_public), repo, edit=True)

    # Filter allow and deny users
    users = [user['name'] for user in
             db.query('SELECT DISTINCT name FROM users')]

    def _filter_users(to_filter):
        for user in to_filter:
            if user not in users:
                error('user {} doesn\'t exist', user)

    _filter_users(allow_read)
    _filter_users(allow_write)
    _filter_users(deny_read)
    _filter_users(deny_write)

    current_acl = db.query('SELECT * FROM acls WHERE repo = ?', repo)

    # Allow users
    def _allow(perm, who):
        current = [acl['user'] for acl in current_acl
                   if acl['allow_to'] == perm]
        for user in who:
            if user not in current:
                db.query('INSERT INTO acls (repo, user, allow_to) VALUES '
                         '(?, ?, ?)', repo, user, perm, edit=True)
    _allow('read', allow_read)
    _allow('write', allow_write)

    def _deny(perm, who):
        current = [acl['user'] for acl in current_acl
                   if acl['allow_to'] == perm]
        for user in who:
            if user in current:
                db.query('DELETE FROM acls WHERE repo = ? AND user = ? AND '
                         'allow_to = ?', repo, user, perm, edit=True)
    _deny('read', deny_read)
    _deny('write', deny_write)


@cli.command('rename-repo')
@click.argument('origin')
@click.argument('destination')
@click.option('-y', '--yes', help='Skip confirmation', is_flag=True)
@click.pass_context
def rename_repo(ctx, origin, destination, yes):
    """ Rename a repository """
    db = ctx.obj['db']

    # Check if the origin repository exists
    exists = db.query('SELECT * FROM repos WHERE name = ?', origin, one=True)
    if not exists:
        error('the repo {} doesn\'t exist', origin)

    # Check if the destination repository doesn't exist
    exists = db.query('SELECT * FROM repos WHERE name = ?', destination,
                      one=True)
    if exists:
        error('the repo {} already exists', destination)

    if not yes:
        click.echo('Are you sure you want to rename the repo {} to {}? [y/N]'
                   .format(origin, destination), nl=False)
        response = click.getchar()
        click.echo()
        try:
            if not distutils.util.strtobool(response):
                raise ValueError  # Skip to the exception block
        except ValueError:
            exit(0)

    # If the origin doesn't exists, there is less work to do \o/
    try:
        os.rename(ctx.obj['storage']+'/'+origin,
                  ctx.obj['storage']+'/'+destination)
    except FileNotFoundError:
        pass
    except OSError:
        error('can\'t move the packages storage to the new destination')

    # Update the database
    db.query('UPDATE repos SET name = ? WHERE name = ?', destination, origin,
             edit=True)
    db.query('UPDATE acls SET repo = ? WHERE repo = ?', destination, origin,
             edit=True)
    db.query('UPDATE releases SET repo = ? WHERE repo = ?', destination,
             origin, edit=True)


@cli.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def config(ctx, key, value):
    """ Edit the OwnRepo configuration """
    settings = ctx.obj['settings']
    settings[key] = value
    settings.save()


@cli.command()
@click.argument('directory', default='.', required=False)
@click.option('--sample', help='Include sample data', is_flag=True)
@click.pass_context
def init(ctx, directory, sample):
    """ Initialize a storage directory """
    directory = os.path.realpath(directory)  # Convert to the full path

    # If the directory doesn't exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # If the directory is not empty
    if os.listdir(directory):
        error('directory {} is not empty', directory)

    # Create the basic structure
    base = os.path.join(directory, '.ownrepo')
    os.makedirs(base)

    # Init the database
    db = ownrepo.db.Connection(os.path.join(directory, '.ownrepo',
                                            'ownrepo.db'))
    db.load_file(pkg_resources.resource_filename('ownrepo', 'schema.sql'))

    # Create settings file
    open(os.path.join(base, 'settings.yml'), 'w').close()

    # Load settings file
    settings = ConfigFile(directory, 'settings')
    settings['password_salt'] = ownrepo.authentication.random_salt()
    settings['brand'] = 'OwnRepo'
    settings.save()

    # If --sample is provided include some sample data
    if sample:
        password = ownrepo.authentication.hash_password(settings, 'admin',
                                                        'admin')
        db.query('INSERT INTO users (name, password) VALUES (?, ?);', 'admin',
                 password, edit=True)
        db.query('INSERT INTO repos (name, is_public) VALUES (?, ?);',
                 'public', 1, edit=True)
        db.query('INSERT INTO repos (name, is_public) VALUES (?, ?);',
                 'private', 0, edit=True)
        db.query('INSERT INTO acls (repo, user, allow_to) VALUES (?, ?, ?), '
                 '(?, ?, ?), (?, ?, ?);', 'public', 'admin', 'write',
                 'private', 'admin', 'read', 'private', 'admin', 'write',
                 edit=True)

    db.close()


if __name__ == '__main__':
    cli()
