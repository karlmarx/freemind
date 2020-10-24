from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy
import os
import logging

from dotenv import load_dotenv

# make this work with docker and env variables and maybe proxy?
from sqlalchemy.pool import NullPool

# load_dotenv()
# db_username = os.environ.get('DB_USERNAME')
# db_password = os.environ.get('DB_PASSWORD')


basedir = os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger()


def init_connection_engine():
    db_config = {
        # [START cloud_sql_postgres_sqlalchemy_limit]
        # Pool size is the maximum number of permanent connections to keep.
        "pool_size": 5,
        # Temporarily exceeds the set pool_size if no connections are available.
        "max_overflow": 2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # [END cloud_sql_postgres_sqlalchemy_limit]
        # [START cloud_sql_postgres_sqlalchemy_backoff]
        # SQLAlchemy automatically uses delays between failed connection attempts,
        # but provides no arguments for configuration.
        # [END cloud_sql_postgres_sqlalchemy_backoff]
        # [START cloud_sql_postgres_sqlalchemy_timeout]
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        "pool_timeout": 30,  # 30 seconds
        # [END cloud_sql_postgres_sqlalchemy_timeout]
        # [START cloud_sql_postgres_sqlalchemy_lifetime]
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # reestablished
        "pool_recycle": 1800,  # 30 minutes
        # [END cloud_sql_postgres_sqlalchemy_lifetime]
        "client_encoding": "utf8",
    }

    if os.environ.get("DB_HOST"):
        return init_tcp_connection_engine(db_config)
    else:
        return init_unix_connection_engine(db_config)


def init_tcp_connection_engine(db_config):
    # [START cloud_sql_postgres_sqlalchemy_create_tcp]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    # os.system('./cloud_sql_proxy -instances=eighth-orbit-287212:us-east4:freemind=tcp:5432')
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]

    # Extract host and port from db_host
    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    pool = create_engine(
        # Equivalent URL:
        # postgres+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL(
            drivername="postgres+pg8000",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_hostname,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 5432
            database=db_name,  # e.g. "my-database-name"
        ),
        # ... Specify additional properties here.
        # [END cloud_sql_postgres_sqlalchemy_create_tcp]
        **db_config
        # [START cloud_sql_postgres_sqlalchemy_create_tcp]
    )
    # [END cloud_sql_postgres_sqlalchemy_create_tcp]

    return pool


def init_unix_connection_engine(db_config):
    # [START cloud_sql_postgres_sqlalchemy_create_socket]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

    pool = create_engine(
        # Equivalent URL:
        # postgres+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<socket_path>/<cloud_sql_instance_name>/.s.PGSQL.5432
        sqlalchemy.engine.url.URL(
            drivername="postgres+pg8000",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            database=db_name,  # e.g. "my-database-name"
            query={
                "unix_sock": "{}/{}/.s.PGSQL.5432".format(
                    db_socket_dir, cloud_sql_connection_name  # e.g. "/cloudsql"
                )  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
            },
        ),
        # ... Specify additional properties here.
        # [END cloud_sql_postgres_sqlalchemy_create_socket]
        **db_config
        # [START cloud_sql_postgres_sqlalchemy_create_socket]
    )
    # [END cloud_sql_postgres_sqlalchemy_create_socket]

    return pool


# The SQLAlchemy engine will help manage interactions, including automatically
# managing a pool of connections to your database
engine = init_connection_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
