import os

import psycopg2
from dotenv import load_dotenv

# Read the variables from the .env file (like DB_PASSWORD)
load_dotenv()


def get_connection():
    """Open and return a connection to the social_media database."""
    connection = psycopg2.connect(
        host="localhost",
        dbname="social_media",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
    )
    return connection
