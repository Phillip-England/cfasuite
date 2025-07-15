

class CfaLocation:

    def __init__(self, name, number, id=0):
        self.id = id
        self.name = name
        self.number = number

    @staticmethod
    def sql_table():
        return '''
            CREATE TABLE IF NOT EXISTS cfa_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                number INTEGER NOT NULL
            )

        '''

    def sql_insert(self):
        sql = '''INSERT INTO cfa_locations (name, number) VALUES (?, ?)'''
        params = (self.name, self.number,)
        return sql, params
    
    @staticmethod
    def sql_delete_by_id(id: int):
        sql = '''DELETE FROM cfa_locations WHERE id = ?'''
        params = (id,)
        return sql, params
    
    @staticmethod
    def sql_select_one(id: int):
        sql = f'''SELECT * FROM cfa_locations WHERE id = ?'''
        params = (id,)
        return sql, params


    @staticmethod
    def sql_select_all():
        sql = f'''SELECT * FROM cfa_locations'''
        params = ()
        return sql, params
    
    @staticmethod
    def one_from_db_row(row: tuple):
        (id, name, number, ) = row
        return CfaLocation(name, number, id)
    
    @staticmethod
    def many_from_db_rows(rows: list):
        cfa_locations = []
        for row in rows:
            (id, name, number, ) = row
            cfa_location = {
                'id': id,
                'name': name,
                'number': number,
            }
            cfa_locations.append(cfa_location)
        return cfa_locations