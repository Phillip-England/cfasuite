from sqlite3 import Connection, connect

from src.data_employee import Employee
from src.data_cfa_location import CfaLocation

def sqlite_connection(path: str):
    conn: Connection = connect(path)
    return conn

def sqlite_table_employees(path: str):
    conn = sqlite_connection(path)
    cursor = conn.cursor()
    cursor.execute(Employee.sql_table())

def sqlite_table_cfa_locations(path: str):
    conn = sqlite_connection(path)
    cursor = conn.cursor()
    cursor.execute(CfaLocation.sql_table())
