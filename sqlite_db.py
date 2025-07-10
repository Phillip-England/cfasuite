from sqlite3 import Connection, connect

def sqlite_connection(path: str):
    conn: Connection = connect(path)
    return conn

def sqlite_table_employees(path: str):
    conn = sqlite_connection(path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_key INTEGER NOT NULL,
            tp_name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            dept TEXT NOT NULL
        )
    ''')
