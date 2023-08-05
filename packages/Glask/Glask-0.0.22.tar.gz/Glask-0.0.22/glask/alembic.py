from __future__ import unicode_literals, print_function, absolute_import, \
    division
from contextlib import contextmanager

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from alembic import command
from alembic.config import Config
from os import path


@contextmanager
def pg_cursor(database='postgres'):
    with connect(database=database) as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            yield cursor


def parse_dbname(app):
    return app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1].split('?')[0]


@contextmanager
def upgrade(app):
    dbname = parse_dbname(app=app)
    with pg_cursor() as cursor:
        cursor.execute('CREATE DATABASE %s' % dbname)
    project_root = path.join(app.root_path, '..')
    alembic_ini = path.join(project_root, 'alembic.ini')
    alembic_config = Config(file_=alembic_ini)
    alembic_config.set_main_option('script_location',
                                   path.join(project_root, 'alembic'))
    command.upgrade(alembic_config, 'head')
    app.logger.disabled = False
    yield app
    with pg_cursor() as cursor:
        cursor.execute(
            'SELECT pg_terminate_backend(pg_stat_activity.pid) '
            'FROM pg_stat_activity '
            'WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid()',
            (dbname,))
        cursor.execute('DROP DATABASE %s' % dbname)
