import os

from .DataSession import *
from .DataCfaLocation import *
from .DataEmployee import *

from sqlite3 import Connection, connect

SQLITE_ABSOLUTE_PATH = os.getenv('SQLITE_ABSOLUTE_PATH')

def sqlite_connection():
    print(SQLITE_ABSOLUTE_PATH)
    conn: Connection = connect(SQLITE_ABSOLUTE_PATH)
    return conn

def sqlite_connection():
    conn: Connection = connect(SQLITE_ABSOLUTE_PATH)
    return conn

def init_tables():
    init_conn = sqlite_connection()
    init_cursor = init_conn.cursor()
    DataCfaLocation.sqlite_create_table(init_cursor)
    DataEmployee.sqlite_create_table(init_cursor)
    DataSession.sqlite_create_table(init_cursor)
    init_conn.commit()
    init_conn.close()