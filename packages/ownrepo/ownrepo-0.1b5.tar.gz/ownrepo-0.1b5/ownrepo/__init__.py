#!python3
import os

import flask
import gunicorn.app.base

from ownrepo.repositories import RepositoriesManager
from ownrepo.web import web
from ownrepo.db import Connection

__version__ = "0.1b5"

version = __version__
storage_version = "2"


class GunicornApplication(gunicorn.app.base.BaseApplication):
    """ A gunicorn application running ownrepo """

    def __init__(self, storage, options=None):
        self.options = options if options is not None else {}
        self.app = create_app(storage)  # Crete a new OwnRepo application

        super(GunicornApplication, self).__init__()

    def load_config(self):
        # Do some cleanup to config items
        config = {key: value for key, value in self.options.items() if key
                  in self.cfg.settings and value is not None}

        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.app


def create_app(storage):
    """ Create a new instance of ownrepo """
    app = flask.Flask(__name__, static_url_path='/+assets')
    app.url_map.strict_slashes = False
    app.ownrepo_storage = storage
    app.ownrepo_db_path = os.path.join(storage, '.ownrepo', 'database')

    def get_db():
        db = getattr(flask.g, '_db', None)
        if db is None:
            db = Connection(flask.current_app.ownrepo_db_path)
            flask.g._db = db
        return db
    app.ownrepo_db = get_db

    def get_settings():
        settings = getattr(flask.g, 'settings', None)
        if settings is None:
            # Retrieve settings
            db = Connection(app.ownrepo_db_path)
            settings_raw = db.query('SELECT key, value FROM settings')
            settings = {o['key']: o['value'] for o in settings_raw}
            flask.g.settings = settings
        return settings
    app.ownrepo_settings = get_settings

    @app.teardown_appcontext
    def _(*args):
        db = getattr(flask.g, '_db', None)
        if db is not None:
            db.close()

    @app.before_request
    def _(*args):
        flask.g.settings = app.ownrepo_settings()
        flask.g.ownrepo_version = __version__

    app.ownrepo_repos = RepositoriesManager(app)

    # Register blueprints
    app.register_blueprint(web)
    return app


def create_gunicorn_process(storage, options=None):
    """ Create a production-ready webserver object using gunicorn """
    if options is None:
        options = {'bind': '0.0.0.0', 'port': 80, 'workers': 3}

    app = GunicornApplication(storage, options)
    return app
