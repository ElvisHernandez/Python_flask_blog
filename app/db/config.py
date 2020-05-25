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

class CRUD:
    @staticmethod
    def _check(table,id,value):
        try:
            conn = g.db
            cursor = conn.cursor()
            sql_query = sql.SQL('''SELECT * FROM {} WHERE {}
            = %s''').format(sql.Identifier(table),
            sql.Identifier(id))
            cursor.execute(sql_query,(value,))
            matches = cursor.fetchall()

            cursor.close()
            return matches
        except psycopg2.Error as e:
            print ('something went wrong in the check function from the CRUD class: ',e)
            return None
    
    @staticmethod
    def _insert(table,**kwargs):
        try:
            conn = g.db
            cursor = conn.cursor()
            keys = tuple(kwargs.keys())
            values = tuple(kwargs.values())
            
            insert_params = ''
            insert_args = ''
            for i in range(len(keys)):
                if i == len(keys) - 1:
                    insert_params += ' {}'
                    insert_args += ' %s'
                else:
                    insert_params += " {}, "
                    insert_args += " %s, "
            insert_args = "(" + insert_args + ")"
            insert_params = ("(" + insert_params + ")").format(*keys)

            sql_insert = '''INSERT INTO {} {} VALUES {} RETURNING id;'''.format(table,insert_params,insert_args)
            cursor.execute(sql_insert, values)
            primary_key = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return primary_key
        except psycopg2.Error as e:
            print ('Something went wrong in the _insert method from the CRUD class: ',e)
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
            print ('This is the deleted row: ',deleted)

            cursor.close()
        except psycopg2.Error as e:
            print ('Something went wrong in the _delete method in the CRUD class: ',e)

    @staticmethod
    def _update(table,primary_key,prop_dict):
        try:
            conn = g.db 
            sql_string = ''
            fields = []
            values = (*tuple(prop_dict.values()), primary_key) 
            for col in prop_dict:
                sql_string += '{} = %s, '
                fields.append(sql.Identifier(col))
            sql_string = sql_string[:-2]

            cursor = conn.cursor()
            sql_string = 'UPDATE {} SET {} WHERE id = %s'.format('{}', sql_string)
            sql_update = sql.SQL(sql_string).format(
               sql.Identifier(table),*fields)

            cursor.execute(sql_update,values)
            conn.commit()
            print ('The _update method was successful')
            cursor.close()
        except psycopg2.Error as e:
            print ('Something went wrong in the _update method from the CRUD class')

