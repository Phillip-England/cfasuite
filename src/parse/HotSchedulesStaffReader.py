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

                    # here is where we set employee departments
                    # departments are based on precedence
                    # precedence order is listed here
                    # order is least important to most important
                    # on the righthanded side of the "-" (next to the departments below)
                    # this represents the job code in hotschedules which maps to the listed department
                    # INIT - should not have any init, if we do, we failed to set a job code in hotschedules
                    # NONE - a single '-' will be in the job code cell for the employee if they are not working at the store
                    # TRAINING - 'In Training'
                    # FOH - 'FOH'
                    # BOH - 'BOH'
                    # RLT - 'Front Counter Stager'
                    # CST - 'Lemons'
                    # EXECUTIVE - 'Mobile Drinks'
                    # PARTNER - 'Dispatcher'

                    depeartment = EmployeeDepartment.INIT
                    if employee_jobs.text == "-":
                        depeartment = EmployeeDepartment.NONE
                    else:
                        tooltip_attr = employee_jobs.find("span").get("tooltip")
                        # single word attrs
                        if tooltip_attr == None:
                            job = employee_jobs.text
                            if 'In Training' in job:
                                depeartment = EmployeeDepartment.TRAINING
                            if "FOH" in job:
                                depeartment = EmployeeDepartment.FOH
                            if "BOH" in job:
                                depeartment = EmployeeDepartment.BOH
                            if 'Front Counter Stager' in job:
                                depeartment = EmployeeDepartment.RLT
                            if 'Lemons' in job:
                                depeartment = EmployeeDepartment.CST
                            if 'Mobile Drinks' in job:
                                depeartment = EmployeeDepartment.EXECUTIVE
                            if 'Dispatcher' in job:
                                depeartment = EmployeeDepartment.PARTNER
                            if depeartment == "":
                                depeartment = EmployeeDepartment.INIT
                        # jobs found in the tooltip attr
                        else:
                            if 'In Training' in tooltip_attr:
                                depeartment = EmployeeDepartment.TRAINING
                            if "FOH" in tooltip_attr:
                                depeartment = EmployeeDepartment.FOH
                            if "BOH" in tooltip_attr:
                                depeartment = EmployeeDepartment.BOH
                            if 'Front Counter Stager' in tooltip_attr:
                                depeartment = EmployeeDepartment.RLT
                            if 'Lemons' in tooltip_attr:
                                depeartment = EmployeeDepartment.CST
                            if 'Mobile Drinks' in tooltip_attr:
                                depeartment = EmployeeDepartment.EXECUTIVE
                            if 'Dispatcher' in tooltip_attr:
                                depeartment = EmployeeDepartment.PARTNER
                            if depeartment == "":
                                depeartment = EmployeeDepartment.INIT
                    Employee.sqlite_update_department(c, employee.id, depeartment)

        #     print(employee_name, "\n", depeartment)
        # print(rows)
