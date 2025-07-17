from sqlite3 import Connection, connect, Cursor

def sqlite_connection(path: str):
    conn: Connection = connect(path)
    return conn

def sqlite_table_cfa_locations(path: str):
    conn = sqlite_connection(path)
    cursor = conn.cursor()
    cursor.execute(CfaLocation.sql_table())

class DataEmployee:
    def __init__(self, id, cfa_location_id, time_punch_name, department):
        self.id = id
        self.cfa_location_id = cfa_location_id
        self.time_punch_name = time_punch_name
        self.department = department
    
    @staticmethod
    def sqlite_create_table(c: Cursor):
        sql = '''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cfa_location_id INTEGER NOT NULL,
                time_punch_name TEXT NOT NULL,
                department TEXT NOT NULL
            )
        '''
        c.execute(sql)
    
    @staticmethod
    def sqlite_insert_one(
        c: Cursor,
        time_punch_name: str,
        department: str,
        cfa_location_id: str
    ):
        sql = f'''INSERT INTO employees (time_punch_name, department, cfa_location_id) VALUES (?, ?, ?)'''
        params = (time_punch_name, department, cfa_location_id,)
        c.execute(sql, params)
        return DataEmployee(c.lastrowid, cfa_location_id, time_punch_name, department)

    @staticmethod
    def sqlite_find_by_time_punch_name(c: Cursor, time_punch_name: str):
        sql = f'''SELECT * FROM employees WHERE time_punch_name = ?'''
        params = (time_punch_name,)
        c.execute(sql, params)
        row = c.fetchone()
        if row == None:
            return None
        (id, cfa_location_id, time_punch_name, department) = row
        return DataEmployee(id, cfa_location_id, time_punch_name, department)

    @staticmethod
    def sqlite_find_by_id(c: Cursor, id: str):
        sql = f'''SELECT * FROM employees WHERE id = ?'''
        params = (id,)
        c.execute(sql, params)
        row = c.fetchone()
        if row == None:
            return None
        (id, cfa_location_id, time_punch_name, department) = row
        return DataEmployee(id, cfa_location_id, time_punch_name, department)

    @staticmethod
    def sqlite_find_all_by_cfa_location_id(c: Cursor, cfa_location_id: str):
        sql = f'''SELECT * FROM employees WHERE cfa_location_id = ?'''  
        params = (cfa_location_id,)
        c.execute(sql, params)
        rows = c.fetchall()
        out = []
        for row in rows:
            (id, cfa_location_id, time_punch_name, department) = row
            out.append(DataEmployee(id, cfa_location_id, time_punch_name, department))
        return out

    @staticmethod
    def sqlite_delete_by_id(c: Cursor, id: str):
        sql = 'DELETE FROM employees WHERE id = ?'
        params = (id,)
        c.execute(sql, params)
        return c.rowcount
    
    @staticmethod
    def sqlite_update_department(c: Cursor, id: str, department: str):
        sql = 'UPDATE employees SET department = ? WHERE id = ?'
        params = (department, id)
        c.execute(sql, params)
        return c.rowcount




class DataCfaLocation:
    def __init__(self, id, name, number):
        self.id = id
        self.name = name
        self.number = number
    
    @staticmethod
    def sqlite_create_table(c: Cursor):
        sql = '''
            CREATE TABLE IF NOT EXISTS cfa_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                number INTEGER NOT NULL
            )
        '''
        c.execute(sql)
    
    @staticmethod
    def sqlite_insert_one(
        c: Cursor,
        name: str,
        number: str,
    ):
        sql = '''INSERT INTO cfa_locations (name, number) VALUES (?, ?)'''
        params = (name, number,)
        c.execute(sql, params)
        return c.lastrowid

    @staticmethod
    def sqlite_delete_by_id(c: Cursor, id: str):
        sql = '''DELETE FROM cfa_locations WHERE id = ?'''
        params = (id,)
        c.execute(sql, params)
        return c.rowcount

    @staticmethod
    def sqlite_find_by_id(c: Cursor, id: str):
        sql = f'''SELECT * FROM cfa_locations WHERE id = ?'''
        params = (id,)
        c.execute(sql, params)
        row = c.fetchone()
        if row == None:
            return None
        (id, name, number) = row
        return DataCfaLocation(id, name, number)

    @staticmethod
    def sqlite_find_by_number(c: Cursor, number: str):
        sql = 'SELECT * FROM cfa_locations WHERE number = ?'
        params = (number,)
        c.execute(sql, params)
        row = c.fetchone()
        if row == None:
            return None
        (id, name, number) = row
        return DataCfaLocation(id, name, number)

    @staticmethod
    def sqlite_find_all(c: Cursor):
        sql = f'''SELECT * FROM cfa_locations'''
        params = ()
        c.execute(sql, params)
        rows = c.fetchall()
        out = []
        for row in rows:
            (id, name, number) = row
            out.append(DataCfaLocation(id, name, number))
        return out

