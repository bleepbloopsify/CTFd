from flask import current_app as app
from flask_migrate import Migrate, migrate, upgrade, stamp, current
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import (
    database_exists as database_exists_util,
    create_database as create_database_util,
    drop_database as drop_database_util
)
from six import StringIO

migrations = Migrate()


def create_database():
    url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
    if url.drivername == 'postgres':
        url.drivername = 'postgresql'

    if url.drivername.startswith('mysql'):
        url.query['charset'] = 'utf8mb4'

    # Creates database if the database database does not exist
    if not database_exists_util(url):
        if url.drivername.startswith('mysql'):
            create_database_util(url, encoding='utf8mb4')
        else:
            create_database_util(url)
    return url


def drop_database():
    url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
    if url.drivername == 'postgres':
        url.drivername = 'postgresql'
    drop_database_util(url)


def get_current_revision():
    engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'), pool_size=0) # no pool defaults
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    current_rev = context.get_current_revision()
    return current_rev
