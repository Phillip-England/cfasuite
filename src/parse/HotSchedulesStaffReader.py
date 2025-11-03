from sqlite3 import Cursor

from bs4 import BeautifulSoup

from ..db import Employee, EmployeeDepartment


class HotSchedulesStaffReader:
    def __init__(self):
        return

    @staticmethod
    async def new(c: Cursor, html: str, employees: list[Employee]):
        soup = BeautifulSoup(html, "html.parser")
        staff_table = soup.find(id="stafftable")
        rows = staff_table.find_all("tr")
        for employee in employees:
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue
                employee_name = cols[1].text.strip()
                if employee.name == employee_name:
                    employee_jobs = cols[6]
                    depeartment = EmployeeDepartment.init().department
                    if employee_jobs.text == "-":
                        depeartment = EmployeeDepartment.none().department
                    else:
                        tooltip_attr = employee_jobs.find("span").get("tooltip")
                        # single word attrs
                        if tooltip_attr == None:
                            job = employee_jobs.text
                            if "FOH" in job:
                                depeartment = EmployeeDepartment.foh().department
                            if "BOH" in job:
                                depeartment = EmployeeDepartment.boh().department
                            if depeartment == "":
                                depeartment = EmployeeDepartment.init().department
                        # jobs found in the tooltip attr
                        else:
                            if "FOH" in tooltip_attr:
                                depeartment = EmployeeDepartment.foh().department
                            if "BOH" in tooltip_attr:
                                depeartment = EmployeeDepartment.boh().department
                            if depeartment == "":
                                depeartment = EmployeeDepartment.init().department
                    Employee.sqlite_update_department(c, employee.id, depeartment)

        #     print(employee_name, "\n", depeartment)
        # print(rows)
