import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import logging
from dotenv import load_dotenv
import os

load_dotenv(encoding="utf-8")

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST")
            )
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    @contextmanager
    def get_connection(self):
        try:
            yield self.connection
        except Exception as e:
            logger.error(f"Error with database connection: {e}")
            raise
        finally:
            try:
                self.connection.commit()
            except Exception as e:
                logger.error(f"Failed to commit transaction: {e}")

    def close(self):
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            logger.info("Database connection closed")

db = Database()