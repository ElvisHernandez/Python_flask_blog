'Load config from enviorment variables.'
import os
from flask import g
import sys
from dotenv import load_dotenv
#from loguru import logger
import logging 
import psycopg2 
from psycopg2 import sql
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s:%(funcName)s:%(message)s')	
file_handler = logging.FileHandler('db.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class Config:
    "Database config"
    DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')

    'This is where the SQL queries live'
    SQL_QUERIES_FOLDER = os.environ.get('SQL_QUERIES_FOLDER')

    TABLES = ['users','roles','posts']


class Database(Config):
    def __init__(self):
        self.username = self.DATABASE_USERNAME
        self.dbname = self.DATABASE_NAME
        self.tables = self.TABLES
        self.conn = None

    def connection(self):
        "connect to a postgres database"
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(user=self.username,
                                             dbname=self.dbname)
                return self.conn
            except psycopg2.DatabaseError as e:
                logger.exception('There was an error connecting to the database: ',e)
                sys.exit()
                return None

            finally:
                logger.info('Connection opened successfully.')

    def init_db(self):
        'creates the database tables via the schema.sql file'
        cursor = self.conn.cursor()
        cursor.execute(open('./db/schema.sql').read())
        self.conn.commit()

    def get_db(self):
        if not hasattr(g, 'db'):
            if self.conn is None:
                self.connection()
            g.db = self.conn
        return g.db

class CRUD:
    @staticmethod
    def _check(table,unique_key,value):
        try:
            conn = g.db
            cursor = conn.cursor()
            if type(value) is int:
                sql_query = sql.SQL('''SELECT * FROM {} WHERE {}
                    = %s''').format(sql.Identifier(table),
                    sql.Identifier(unique_key))
            else:
                sql_query = sql.SQL('''SELECT * FROM {} WHERE lower({})
                    = %s''').format(sql.Identifier(table),
                    sql.Identifier(unique_key))
                
            cursor.execute(sql_query,(value,))
            matches = cursor.fetchone()
            cursor.close()

            if matches is None:
                return None
            props = [desc[0] for desc in cursor.description]
            prop_dict = dict(zip(props,matches))

            return prop_dict
        except psycopg2.Error as e:
            logger.exception('something went wrong in the check function from the CRUD class: ',e)
            return None
    
    @staticmethod
    def _insert(table,**kwargs):
        try:
            conn = g.db
            cursor = conn.cursor()
            if "role_id" in kwargs and kwargs['role_id'] is None:
                sql_role_default = '''SELECT id FROM roles WHERE "default" = TRUE;'''
                cursor.execute(sql_role_default)
                default_role = cursor.fetchone()[0]
                kwargs['role_id'] = default_role

            values = tuple(kwargs.values())
            insert_params = ''
            insert_args = ''
            fields = []
            for field in kwargs:
                fields.append(sql.Identifier(field))
                insert_params += '{}, '
                insert_args += '%s, '

            insert_args = "(" + insert_args[:-2] + ")"
            insert_params = "(" + insert_params[:-2] + ")"
            sql_insert = '''INSERT INTO {} {} VALUES {} RETURNING id;'''.format('{}',insert_params,insert_args)

            sql_insert = sql.SQL(sql_insert).format(sql.Identifier(table),*fields)
            cursor.execute(sql_insert, values)
            primary_key = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return primary_key
        except psycopg2.Error as e:
            logger.exception('Something went wrong in the _insert method from the CRUD class: ',e)
            return None

    @staticmethod
    def _delete(table,id):
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_delete = sql.SQL('''DELETE FROM {} WHERE id = %s RETURNING id
            ;''').format(sql.Identifier(table))
            cursor.execute(sql_delete,(id,))
            deleted = cursor.fetchone()
            conn.commit()

            cursor.close()
        except psycopg2.Error as e:
            logger.exception('Something went wrong in the _delete method in the CRUD class: ',e)

    @staticmethod
    def _update(table,unique_id,prop_dict):
        try:
            conn = g.db 
            sql_string = ''
            fields = []
            values = (*tuple(prop_dict.values()), unique_id) 
            for col in prop_dict:
                sql_string += '{} = %s, '
                fields.append(sql.Identifier(col))
            sql_string = sql_string[:-2]

            cursor = conn.cursor()
            sql_string = 'UPDATE {} SET {} WHERE id = %s RETURNING *;'.format('{}', sql_string)

            sql_update = sql.SQL(sql_string).format(
               sql.Identifier(table),*fields)

            cursor.execute(sql_update,values)
            row = cursor.fetchone()

            conn.commit()
            cursor.close()
            return row
        except psycopg2.Error as e:
            logger.exception('Something went wrong in the _update method from the CRUD class: ',e)
            return None

#placed at the bottom to avoid circular import
from .UserModel import User
