#!python3
import functools

import flask

import ownrepo.repositories
import ownrepo.authentication


web = flask.Blueprint('web', __name__)


def check_auth(repo_key=None, write=False):
    """ Process the request only if the user is logged in """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            repos = flask.current_app.ownrepo_repos
            # If a repo_key is specified require auth only if
            # that repository is private
            if repo_key is not None:
                requested_repo = kwargs[repo_key]
                if not repos.exists(requested_repo):
                    return flask.abort(404)
                try:
                    # This won't raise an exception if the user can access the
                    # requested repository
                    repo = repos.get(requested_repo)
                    if write and not repo.writable:
                        raise ValueError  # Jump to the except block
                except ValueError:
                    # If the user isn't authenticated trigger the HTTP auth
                    if getattr(flask.g, 'authenticated_as', None) is None:
                        return ownrepo.authentication.trigger_http_auth()
                    else:
                        return flask.abort(403)
                else:
                    return f(*args, **kwargs)
            else:
                if 'authenticated_as' not in flask.g:
                    return ownrepo.authentication.trigger_http_auth()
                else:
                    return f(*args, **kwargs)
        return wrapper
    return decorator


@web.before_request
def validate_auth():
    """ Log in the user only if HTTP auth is correct, else do nothing """
    auth = flask.request.authorization
    if auth:
        db = flask.current_app.ownrepo_db()
        settings = flask.current_app.ownrepo_settings()
        name = auth.username
        password = auth.password
        if not ownrepo.authentication.validate(settings, db, name, password):
            pass
        else:
            flask.g.authenticated_as = name


@web.route('/')
def home():
    """ Home page of ownrepo """
    repos = flask.current_app.ownrepo_repos
    repos_list = repos.list()
    return flask.render_template('home.html', repos=repos_list)


@web.route('/<repo>')
@check_auth('repo')
def repo(repo):
    repos = flask.current_app.ownrepo_repos
    try:
        repo = repos.get(repo)
    except ValueError:
        return flask.abort(404)
    else:
        return flask.render_template('repo.html', repo=repo)


@web.route('/<repo>/<package>')
@check_auth('repo')
def package(repo, package):
    repos = flask.current_app.ownrepo_repos
    try:
        package = repos.get(repo).all_packages[package]
    except (ValueError, KeyError):
        return flask.abort(404)
    else:
        return flask.render_template('package.html', package=package,
                                     repo=repo)


@web.route('/<repo>/<package>/<release>')
@check_auth('repo')
def release(repo, package, release):
    repos = flask.current_app.ownrepo_repos
    try:
        package = repos.get(repo).all_packages[package]
    except (ValueError, KeyError):
        return flask.abort(404)
    else:
        if release not in package.releases:
            return flask.abort(404)

        return flask.render_template('release.html', repo=repo,
                                     package=package, release=release)


@web.route('/<repo>/<package>/+download/<file>')
@check_auth('repo')
def download(repo, package,  file):
    base = flask.current_app.ownrepo_storage
    repos = flask.current_app.ownrepo_repos

    try:
        package = repos.get(repo).all_packages[package]
    except (ValueError, KeyError):
        return flask.abort(404)

    repo_dir = package.repo.name
    return flask.send_from_directory(base+'/'+repo_dir, file)


@web.route('/<repo>/+simple', methods=['GET'])
@check_auth('repo')
def simple_repo(repo):
    repos = flask.current_app.ownrepo_repos
    try:
        repo = repos.get(repo)
    except ValueError:
        return flask.abort(404)
    else:
        return flask.render_template('simple_repo.html', repo=repo)


@web.route('/<repo>/+simple', methods=['POST'])
@check_auth('repo', write=True)
def simple_manage(repo):
    repos = flask.current_app.ownrepo_repos
    try:
        repo = repos.get(repo)
    except ValueError:
        return flask.abort(404)

    data = flask.request.form

    # Upload file
    if data[':action'] == 'file_upload':
        # Collect some useful informations
        package_name = data['name'].lower()
        version = data['version']
        md5 = data['md5_digest']
        archive_type = data['filetype']
        archive = flask.request.files['content']

        # Create the package if it doesn't exist
        if package_name not in repo.packages:
            repo.create_package(package_name)

        # Add the new archive to the repository
        package = repo.packages[package_name]
        package.add_release(version, archive_type, archive, md5)

        return 'Package uploaded'
    else:
        return flask.abort(400, 'Unsupported action')


@web.route('/<repo>/+simple/<package>')
@check_auth('repo')
def simple_package(repo, package):
    repos = flask.current_app.ownrepo_repos
    try:
        package = repos.get(repo).all_packages[package]
    except (ValueError, KeyError):
        return flask.abort(404)
    else:
        return flask.render_template('simple_package.html', package=package,
                                     repo=repo)


@web.route('/+login')
@check_auth()
def login():
    return flask.redirect(flask.url_for('web.home'))


@web.errorhandler(404)
def not_found(e):
    return flask.render_template('not_found.html'), 404
