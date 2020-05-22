'Load config from enviorment variables.'
import os
from flask import g
import sys
from dotenv import load_dotenv
from loguru import logger
import psycopg2 
from psycopg2 import sql

load_dotenv()


class Config:
    "Database config"
    DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')

    'This is where the SQL queries live'
    SQL_QUERIES_FOLDER = os.environ.get('SQL_QUERIES_FOLDER')

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

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute(open('./db/schema.sql').read())
        self.conn.commit()

    def get_db(self):
        if not hasattr(g, 'db'):
            if self.conn is None:
                self.connection()
            g.db = self.conn
        return g.db

def check_user(user,table, db_connection):
    cursor = db_connection.cursor()
    sql_query = sql.SQL('SELECT * FROM {} WHERE username = %s;').format(sql.Identifier(table))

    cursor.execute(sql_query, (user,))
    result = cursor.fetchall()
    if len(result) == 0:
        sql_insert = sql.SQL('INSERT INTO {} (username,role_id) VALUES (%s,%s)').format(sql.Identifier(table))
        cursor.execute(sql_insert, (user, 3))
        db_connection.commit()
        send_email(os.environ.get('ADMIN_EMAIL'),
                   'New User', 'mail/new_user', name=user)
        return False
    else:
        return True

from ..email import send_email