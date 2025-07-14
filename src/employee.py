
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
    def __init__(self, tp_name: str):
        self.id = 0
        self.tp_name = tp_name
        name_parts = self.tp_name.split(',')
        self.full_name = f"{name_parts[1]} {name_parts[0]}"
        self.department = EmployeeDepartment("INIT")
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
    
    def sql_insert(self):
        sql = f'''INSERT INTO employees (tp_name, full_name, department) VALUES (?, ?, ?)'''
        params = (self.tp_name, self.full_name, self.department.name,)
        return sql, params
    
    def sql_find(self):
        sql = f'''SELECT * FROM employees WHERE tp_name = ?'''
        params = (self.tp_name,)
        return sql, params
    
    @staticmethod
    def sql_all():
        sql = f'''SELECT * FROM employees'''  
        params = ()
        return sql, params

    @staticmethod
    def many_from_db_rows(rows: list):
        employees = []
        for row in rows:
            (id, tp_name, full_name, department) = row
            employee = {
                'id': id,
                'tp_name': tp_name,
                'full_name': full_name,
                'department': department,
            }
            employees.append(employee)
        return employees

    @staticmethod
    def sql_table():
        return '''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tp_name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL
            )
        '''