"""
app.py

A common utility app for flask

Contain common view interface

-. LoginManager
-. UserManager
-. Error
"""

import os
import re
import functools
import jinja2
import redis
from utils import is_valid_email, is_valid_password, hash_string, \
    verify_hash_string, generate_random_string, to_currency, to_slug, \
    add_path_to_jinja
from flask import abort
from flask.ext.login import current_user
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
import humanize
import mistune

# ------------------------------------------------------------------------------

__version__ = "0.22.0"



def get_redis(dsn):
    """
    Return the redis connection
    :param dsn: The dsn url
    :return: Redis
    """
    return redis.StrictRedis.from_url(url=dsn)

def with_user_roles(roles):
    """
    with_user_roles(roles)

    It allows to check if a user has access to a view by adding the decorator
    with_user_roles([])

    Requires flask-login

    In your model, you must have a property 'role', which will be invoked to
    be compared to the roles provided.

    If current_user doesn't have a role, it will throw a 403

    If the current_user is not logged in will throw a 401

    * Require Flask-Login
    ---
    Usage

    @app.route('/user')
    @login_require
    @with_user_roles(['admin', 'user'])
    def user_page(self):
        return "You've got permission to access this page."
    """
    def wrapper(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.is_authenticated():
                if not hasattr(current_user, "role"):
                    raise AttributeError("<'role'> doesn't exist in login 'current_user'")
                if current_user.role not in roles:
                    return abort(403)
            else:
                return abort(401)
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def with_user_rights(*roles):
    """
    with_user_right(*roles)

    It allows to check if a user has access to a view by adding the decorator
    with_user_rights(*roles)

    Using accept_user_roles() requires flask-login.

    In your model, you must have a property 'role', which will be invoked to
    be compared to the roles provided.

    If current_user doesn't have a role, it will throw a 403

    If the current_user is not logged in will throw a 401

    * Require Flask-Login
    ---
    Usage

    @app.route('/user')
    @login_require
    @with_user_roles('admin', 'user')
    def user_page(self):
        return "You've got permission to access this page."
    """
    def wrapper(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.is_authenticated():
                if not hasattr(current_user, "riles"):
                    raise AttributeError("<'rights'> doesn't exist in login 'current_user'")
                if current_user.rights not in roles:
                    return abort(403)
            else:
                return abort(401)
            return f(*args, **kwargs)
        return wrapped
    return wrapper

class AdminRoleMixin(object):
    pass

class AppError(Exception):
    """ For exception in application pages """
    pass


class Session(object):
    """ Set the Session. Using KVSession """
    def __init__(self, app):
        _redis = get_redis(app.config.get("KVSESSION_REDIS_DSN"))
        store = RedisStore(_redis)
        KVSessionExtension(store, app)

class NewRelic(object):
    def __init__(self, app):
        import newrelic.agent
        newrelic.agent.initialize()
        settings = newrelic.agent.global_settings()
        settings.license_key = app.config.get("NEWRELIC_LICENSE_KEY")
        settings.app_name = app.config.get("NEWRELIC_APP_NAME")
        settings.monitor_mode = True
        settings.log_level = "info"
        settings.ssl = True
        settings.transaction_tracer.enabled = True
        settings.transaction_tracer.transaction_threshold = "apdex_f"
        settings.transaction_tracer.record_sql = "obfuscated"
        settings.error_collector.enabled = False
        settings.slow_sql.enabled = False
        settings.browser_monitoring.auto_instrument = False

# ------------------------------------------------------------------------------
# FILTERS

def to_date(dt, format="%m/%d/%Y"):
    return dt.strftime(format)

def strip_decimal(amount):
    return amount.split(".")[0]

def bool_to_yes(b):
    return "Yes" if b is True else "No"

def bool_to_int(b):
    return 1 if b is True else 0

def nl2br(s):
    """
    {{ s|nl2pbr }}

    Convert newlines into <p> and <br />s.
    """
    if not isinstance(s, basestring):
        s = str(s)
    s = re.sub(r'\r\n|\r|\n', '\n', s)
    paragraphs = re.split('\n{2,}', s)
    paragraphs = ['<p>%s</p>' % p.strip().replace('\n', '<br />') for p in paragraphs]
    return '\n\n'.join(paragraphs)

def to_filesize(i):
    """
    {{ i|filesizeformat }}

    Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    bytes = float(i)
    if bytes < 1024:
        return u"%d Byte%s" % (bytes, bytes != 1 and u's' or u'')
    if bytes < 1024 * 1024:
        return u"%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return u"%.1f MB" % (bytes / (1024 * 1024))
    return u"%.1f GB" % (bytes / (1024 * 1024 * 1024))

jinja2.filters.FILTERS.update({
    "to_currency": to_currency,
    "strip_decimal": strip_decimal,
    "to_date": to_date,
    "to_int": int,
    "to_slug": to_slug,
    "to_intcomma": humanize.intcomma,
    "to_intword": humanize.intword,
    "to_naturalday": humanize.naturalday,
    "to_naturaldate": humanize.naturaldate,
    "to_naturaltime": humanize.naturaltime,
    "markdown": mistune.markdown,
    "bool_to_yes": bool_to_yes,
    "bool_to_int": bool_to_int,
    "nl2br": nl2br,
    "to_filesize": to_filesize
})
