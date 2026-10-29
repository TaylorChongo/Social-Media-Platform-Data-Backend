import os

import redis
from dotenv import load_dotenv
from psycopg2 import pool
from pymongo import MongoClient

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


# Redis: fast in-memory cache for timelines (Memurai on Windows)
# decode_responses=True gives us normal strings instead of bytes
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# MongoDB: activity logs (the database and collection are created on first use)
mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["social_media"]
activity_logs = mongo_db["activity_logs"]
