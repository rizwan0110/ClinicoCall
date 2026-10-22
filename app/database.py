import logging
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("Database configuration is missing")

    try:
        return psycopg2.connect(DATABASE_URL)
    except psycopg2.Error:
        logger.exception("Failed to connect to the database")
        raise
