import os

from .Session import *
from .Location import *
from .Employee import *

from sqlite3 import Connection, connect

def sqlite_connection(path: str):
    conn: Connection = connect(path)
    return conn, conn.cursor()

def init_tables(path: str):
    init_conn, init_cursor = sqlite_connection(path)
    Location.sqlite_create_table(init_cursor)
    Employee.sqlite_create_table(init_cursor)
    Session.sqlite_create_table(init_cursor)
    init_conn.commit()
    init_conn.close()