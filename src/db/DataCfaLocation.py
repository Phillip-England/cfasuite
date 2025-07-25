from sqlite3 import Cursor

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