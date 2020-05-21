'Load config from enviorment variables.'
from os import environ
import sys
from dotenv import load_dotenv
from loguru import logger
import psycopg2

load_dotenv()


class Config:
    "Database config"
    DATABASE_USERNAME = environ.get('DATABASE_USERNAME')
    DATABASE_NAME = environ.get('DATABASE_NAME')

    'This is where the SQL queries live'
    SQL_QUERIES_FOLDER = environ.get('SQL_QUERIES_FOLDER')

    TABLES = ['users,roles']


class Database:
    def __init__(self, config):
        self.username = config.DATABASE_USERNAME
        self.dbname = config.DATABASE_NAME
        self.conn = None
        self.tables = config.TABLES

    def connection(self):
        "connect to a postgres database"
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(user=self.username,
                                             dbname=self.dbname)
                return self.conn
            except psycopg2.DatabaseError as e:
                logger.error(e)
                sys.exit()

            finally:
                logger.info('Connection opened successfully.')

    def close(self):
        if self.conn is not None:
            self.conn.close()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute(open('./db/schema.sql').read())
        self.conn.commit()
