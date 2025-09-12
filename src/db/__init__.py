import os

from .Session import *
from .Location import *
from .Employee import *

from sqlite3 import Connection, connect

SQLITE_ABSOLUTE_PATH = os.getenv('SQLITE_ABSOLUTE_PATH')
if SQLITE_ABSOLUTE_PATH == None:
    print('you must create a .env file with SQLITE_ABSOLUTE_PATH set to an absolute path')
    exit(1)

def sqlite_connection():
    conn: Connection = connect(SQLITE_ABSOLUTE_PATH)
    return conn

def init_tables():
    init_conn = sqlite_connection()
    init_cursor = init_conn.cursor()
    Location.sqlite_create_table(init_cursor)
    Employee.sqlite_create_table(init_cursor)
    Session.sqlite_create_table(init_cursor)
    init_conn.commit()
    init_conn.close()