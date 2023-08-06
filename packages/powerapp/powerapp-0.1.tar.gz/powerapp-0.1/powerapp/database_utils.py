# -*- coding: utf-8 -*-
"""
Database utils

Database parsing functions are heavily based on @kennethreitz's dj-database-url
"""
import os
import pickle
from base64 import b64encode, b64decode
from six.moves.urllib import parse
import peewee


# Register database schemes in URLs.
parse.uses_netloc.append('postgres')
parse.uses_netloc.append('mysql')
parse.uses_netloc.append('sqlite')


def get_sqlite_database(host='', database='', **config):
    if host and not database:
        database = host
    elif host:  # relative path, host is the first chunk of the name
        database = os.path.join(host, database)
    else:  # absolute path
        database = os.path.join('/', database)

    if not database:
        database = ':memory:'
    return peewee.SqliteDatabase(database=database)


SCHEMES = {
    'mysql': peewee.MySQLDatabase,
    'postgres': peewee.PostgresqlDatabase,
    'sqlite': get_sqlite_database,
}


def url_to_database(url):
    """
    Parses a database URL.

    Sqlite URL have special treatment:

    - sqlite://relative/path.sqlite -- relative path to database
    - sqlite:///absolute/path.sqlite -- absolute path to database

    :rtype: peewee.Database
    """
    if url == 'sqlite://:memory:' or url == 'sqlite:///:memory:':
        # this is a special case, because if we pass this URL into
        # urlparse, urlparse will choke trying to interpret "memory"
        # as a port number
        return SCHEMES['sqlite'](':memory:')
        # note: no other settings are required for sqlite

    # otherwise parse the url as normal
    config = {}

    url = parse.urlparse(url)

    # Remove query strings.
    path = url.path[1:]
    path = path.split('?', 2)[0]

    # Handle postgres percent-encoded paths.
    hostname = url.hostname or ''
    if '%2f' in hostname.lower():
        hostname = hostname.replace('%2f', '/').replace('%2F', '/')

    # Update with environment configuration.
    config.update({
        'database': path or '',
        'user': url.username or '',
        'password': url.password or '',
        'host': hostname,
        'port': url.port or '',
    })
    return SCHEMES[url.scheme](**config)


class PickleField(peewee.BlobField):

    def db_value(self, value):
        return b64encode(pickle.dumps(value))

    def python_value(self, value):
        if value:
            return pickle.loads(b64decode(value))
