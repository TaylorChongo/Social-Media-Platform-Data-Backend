import os

from dotenv import load_dotenv
from psycopg2 import pool

# Read the variables from the .env file (like DB_PASSWORD)
load_dotenv()

# A pool keeps a few connections open so we can reuse them
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host="localhost",
    dbname="social_media",
    user="postgres",
    password=os.getenv("DB_PASSWORD"),
)


def get_connection():
    """Borrow a connection from the pool."""
    return connection_pool.getconn()


def release_connection(connection):
    """Give a connection back to the pool so it can be reused."""
    connection_pool.putconn(connection)
