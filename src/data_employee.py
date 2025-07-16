
from pandas import DataFrame

class EmployeeBioReader:
    def __init__(self, df: DataFrame):
        self.names = []
        for i, row in df.iterrows():
            employee_status = row["Employee Status"]
            if employee_status == "Terminated":
                continue
            name = row["Employee Name"]
            self.names.append(name)


class EmployeeDepartment:
    def __init__(self, name):
        valid_names = ['FOH', 'BOH', 'DIRECTOR', 'INIT']
        if name not in valid_names:
            raise Exception(f"{name} is not a valid EmployeeDepartment")
        self.name = name

class Employee:
    def __init__(self, tp_name: str, cfa_location_id: str, full_name: str | None = None, id: int = 0, department = EmployeeDepartment('INIT')):
        self.id = id
        self.tp_name = tp_name
        self.cfa_location_id = cfa_location_id
        if full_name == None:
            name_parts = self.tp_name.split(',')
            self.full_name = f"{name_parts[1]} {name_parts[0]}"
        self.department = department
    def __str__(self):
        return f"""TP NAME: {self.tp_name}\n
FULL_NAME: {self.full_name}\n
DEPARTMENT: {self.department}\n
"""
    @classmethod
    def new_raw(cls, id, tp_name, full_name, dept):
        employee = cls()
        employee.id = id
        employee.tp_name = tp_name
        employee.full_name = full_name
        employee.department = dept
    
    def sql_insert_one(self):
        sql = f'''INSERT INTO employees (tp_name, full_name, department, cfa_location_id) VALUES (?, ?, ?, ?)'''
        params = (self.tp_name, self.full_name, self.department.name, self.cfa_location_id,)
        return sql, params
    
    def sql_find_by_name(self):
        sql = f'''SELECT * FROM employees WHERE tp_name = ?'''
        params = (self.tp_name,)
        return sql, params
    
    @staticmethod
    def sql_find_by_id(id: str):
        sql = 'SELECT * FROM employees WHERE id = ?'
        params = (id,)
        return sql, params
    
    @staticmethod
    def sql_find_all_by_cfa_location_id(cfa_location_id: int):
        sql = f'''SELECT * FROM employees WHERE cfa_location_id = ?'''  
        params = (cfa_location_id,)
        return sql, params
    
    @staticmethod
    def sql_delete_by_id(id: int):
        sql = 'DELETE FROM employees WHERE id = ?'
        params = (id,)
        return sql, params
    
    @staticmethod
    def one_from_db_row(row: tuple):
        (id, cfa_location_id, tp_name, full_name, department) = row
        employee = Employee(tp_name, cfa_location_id, full_name, id, department)
        return employee

    @staticmethod
    def many_from_db_rows(rows: list):
        employees = []
        for row in rows:
            (id, cfa_location_id, tp_name, full_name, department) = row
            employee = Employee(tp_name, cfa_location_id, full_name, id, department)
            employees.append(employee)
        return employees

    @staticmethod
    def sql_update_department(department: str, id: str):
        sql = 'UPDATE employees SET department = ? WHERE id = ?'
        params = (department, id)
        return sql, params

    @staticmethod
    def sql_table():
        return '''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cfa_location_id_str INTEGER NOT NULL,
                tp_name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL
            )
        '''
    