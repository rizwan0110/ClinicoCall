
import logging
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is missing")
        raise RuntimeError("Database configuration is missing")

    try:
        connection = psycopg2.connect(DATABASE_URL)
        return connection

    except psycopg2.Error:
        logger.exception("Failed to connect to the database")
        raise
