#!python3
import hashlib
import random
import string

import flask


def hash_password(settings, name, password):
    """ Hash a password """
    salted = settings['password_salt']+password+name
    return hashlib.sha512(salted.encode('utf-8')).hexdigest()


def random_salt():
    """ Generate a random salt """
    # Generate a random 32-chars salt
    salt = ''.join(random.SystemRandom().choice(string.printable)
                   for _ in range(32))
    return salt


def validate(settings, db, name, password):
    """ Validate an username-password pair """
    hashed = hash_password(settings, name, password)
    result = db.query('SELECT * FROM users WHERE name = ? AND password = ?',
                      name, hashed, one=True)

    return bool(result)


def trigger_http_auth():
    """ Trigger an HTTP auth """
    brand = flask.current_app.ownrepo_settings()["brand"]
    return flask.Response(flask.render_template('login_failed.html'), 401,
                          {'WWW-Authenticate': 'Basic realm="'+brand+'"'})
