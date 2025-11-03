from sqlite3 import Cursor


class Employee:
    def __init__(self, id, cfa_location_id, time_punch_name, name, department, birthday=""):
        self.id = id
        self.cfa_location_id = cfa_location_id
        self.time_punch_name = time_punch_name
        self.name = name
        self.department = department
        self.birthday = birthday

    @staticmethod
    def sqlite_add_birthday(c: Cursor, id: str, birthday: str):
        sql = "UPDATE employees SET birthday = ? WHERE id = ?"
        params = (birthday, id)
        c.execute(sql, params)
        return c.rowcount

    @staticmethod
    def sqlite_create_table(c: Cursor):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cfa_location_id INTEGER NOT NULL,
                time_punch_name TEXT NOT NULL,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                birthday TEXT
            )
        """
        c.execute(sql)

    @staticmethod
    def sqlite_insert_one(
        c: Cursor,
        time_punch_name: str,
        department: str,
        cfa_location_id: str,
        birthday="",
    ):
        name_parts = time_punch_name.split(',')
        last_name = name_parts[0].removesuffix(' ')
        first_name = name_parts[1]
        first_name = first_name.removeprefix(' ')
        first_name_finalized = ''
        if first_name.count(' ') > 0:
            first_name_finalized += first_name.split(' ')[0].removesuffix(' ').removeprefix(' ')
        else:
            first_name_finalized += first_name.removesuffix(' ').removeprefix(' ')
        name = f'{first_name_finalized} {last_name}' 
        sql = f"""INSERT INTO employees (name, time_punch_name, department, cfa_location_id, birthday) VALUES (?, ?, ?, ?, ?)"""
        params = (
            name,
            time_punch_name,
            department,
            cfa_location_id,
            birthday,
        )
        c.execute(sql, params)
        return Employee(c.lastrowid, cfa_location_id, time_punch_name, name, department)

    @staticmethod
    def sqlite_find_by_time_punch_name(c: Cursor, time_punch_name: str):
        sql = f"""SELECT * FROM employees WHERE time_punch_name = ?"""
        params = (time_punch_name,)
        c.execute(sql, params)
        row = c.fetchone()
        if row == None:
            return None
        (id, cfa_location_id, time_punch_name, name, department) = row
        return Employee(id, cfa_location_id, time_punch_name, name, department)

    @staticmethod
    def sqlite_find_by_id(c: Cursor, id: str):
        sql = f"""SELECT * FROM employees WHERE id = ?"""
        params = (id,)
        c.execute(sql, params)
        row = c.fetchone()
        if row == None:
            return None
        (id, cfa_location_id, time_punch_name, name, department) = row
        return Employee(id, cfa_location_id, time_punch_name, name, department)

    @staticmethod
    def sqlite_find_all_by_cfa_location_id(c: Cursor, cfa_location_id: str):
        sql = f"""SELECT * FROM employees WHERE cfa_location_id = ? ORDER BY time_punch_name ASC"""
        params = (cfa_location_id,)
        c.execute(sql, params)
        rows = c.fetchall()
        out = []
        for row in rows:
            (id, cfa_location_id, time_punch_name, name, department, birthday) = row
            out.append(
                Employee(id, cfa_location_id, time_punch_name, name, department, birthday)
            )
        return out

    @staticmethod
    def sqlite_delete_by_id(c: Cursor, id: str):
        sql = "DELETE FROM employees WHERE id = ?"
        params = (id,)
        c.execute(sql, params)
        return c.rowcount

    @staticmethod
    def sqlite_update_department(c: Cursor, id: str, department: str):
        sql = "UPDATE employees SET department = ? WHERE id = ?"
        params = (department, id)
        c.execute(sql, params)
        return c.rowcount
