

class CfaLocation:

    def __init__(self, name, number):
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
    def sql_all():
        sql = f'''SELECT * FROM cfa_locations'''
        params = ()
        return sql, params
    

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