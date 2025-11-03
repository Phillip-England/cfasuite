from io import BytesIO
from sqlite3 import Connection, Cursor

from fastapi import UploadFile
from pandas import read_excel

from src.db import Employee, EmployeeDepartment


class EmployeeBioReader:
    def __init__(self, names: slice):
        self.names = names

    @staticmethod
    async def new(file: UploadFile):
        names = []
        file_contents = await file.read()
        df = read_excel(BytesIO(file_contents))
        for i, row in df.iterrows():
            employee_status = row["Employee Status"]
            if employee_status == "Terminated":
                continue
            name = row["Employee Name"]
            names.append(name)
        return EmployeeBioReader(names)

    def insert_all_employees(self, conn: Connection, c: Cursor, cfa_location_id: str):
        current_employees = Employee.sqlite_find_all_by_cfa_location_id(
            c, cfa_location_id
        )
        reader_names = self.names
        for name in reader_names:
            found = False
            for employee in current_employees:
                if name == employee.time_punch_name:
                    found = True
                    break
            if found == False:
                Employee.sqlite_insert_one(c, name, EmployeeDepartment.init().department, cfa_location_id)
        conn.commit()

    def remove_terminated_employees(
        self, conn: Connection, c: Cursor, cfa_location_id: str
    ):
        current_employees = Employee.sqlite_find_all_by_cfa_location_id(
            c, cfa_location_id
        )
        for employee in current_employees:
            found = False
            for name in self.names:
                if name == employee.time_punch_name:
                    found = True
                    break
            if found == False:
                Employee.sqlite_delete_by_id(c, employee.id)
        conn.commit()
