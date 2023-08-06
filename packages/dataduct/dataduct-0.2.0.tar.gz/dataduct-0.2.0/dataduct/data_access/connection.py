"""
Connections to various databases such as RDS and Redshift
"""
import psycopg2
import MySQLdb
import MySQLdb.cursors

from ..config import Config
from ..utils.helpers import retry
from ..utils.helpers import exactly_one
from ..utils.exceptions import ETLConfigError

config = Config()
CONNECTION_RETRIES = config.etl.get('CONNECTION_RETRIES', 2)


def get_redshift_config():
    """Get redshift config from config file and return the dictionary
    """
    if not hasattr(config, 'redshift'):
        raise ETLConfigError('Redshift config not found')
    return config.redshift


@retry(CONNECTION_RETRIES, 60)
def redshift_connection(redshift_creds=None, **kwargs):
    """Fetch a psql connection object to redshift
    """
    if redshift_creds is None:
        redshift_creds = get_redshift_config()

    connection = psycopg2.connect(
        host=redshift_creds['HOST'],
        user=redshift_creds['USERNAME'],
        password=redshift_creds['PASSWORD'],
        port=redshift_creds['PORT'],
        database=redshift_creds['DATABASE_NAME'],
        connect_timeout=10,
        **kwargs)
    return connection


def get_sql_config(database_name):
    """Get SQL config from config file and return the dictionary
    """
    if not hasattr(config, 'mysql'):
        raise ETLConfigError('mysql not found in dataduct configs')

    if database_name not in config.mysql:
        raise ETLConfigError(
            'Config for hostname: %s not found' % database_name)

    sql_creds = config.mysql[database_name]
    sql_creds['DATABASE'] = database_name

    return sql_creds


@retry(CONNECTION_RETRIES, 60)
def rds_connection(database_name=None, sql_creds=None,
                   cursorclass=MySQLdb.cursors.SSCursor, **kwargs):
    """Fetch a mysql connection object to rds databases
    """

    assert exactly_one(database_name, sql_creds), \
        'Either database or params needed'

    if sql_creds is None:
        sql_creds = get_sql_config(database_name)

    connection = MySQLdb.connect(
        host=sql_creds['HOST'],
        user=sql_creds['USERNAME'],
        passwd=sql_creds['PASSWORD'],
        db=sql_creds['DATABASE'],
        charset='utf8',      # Necessary for foreign chars
        cursorclass=cursorclass,
        **kwargs)
    return connection
