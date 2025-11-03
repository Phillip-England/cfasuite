from bs4 import BeautifulSoup
from sqlite3 import Cursor

from io import BytesIO

from ..db import Employee

class HotSchedulesStaffReader:
    def __init__(self):
        return
    
    @staticmethod
    async def new(html: str, employees: list[Employee]):
        soup = BeautifulSoup(html, 'html.parser')
        staff_table = soup.find(id='stafftable')
        rows = staff_table.find_all('tr')
        for employee in employees:
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 7:
                    continue
                employee_name = cols[1].text.strip()
                if employee.name == employee_name:
                    employee_jobs = cols[6]
                    depeartment = ''
                    if employee_jobs.text == '-':
                        depeartment = 'NONE'
                    else:
                        tooltip_attr = employee_jobs.find('span').get('tooltip')
                        # single word attrs
                        if tooltip_attr == None:
                            job = employee_jobs.text
                            if 'FOH' in job:
                                depeartment = 'FOH'
                            if 'BOH' in job:
                                depeartment = 'BOH'
                            if depeartment == '':
                                depeartment = 'INIT'
                        # jobs found in the tooltip attr
                        else:
                            if 'FOH' in tooltip_attr:
                                depeartment = 'FOH'
                            if 'BOH' in tooltip_attr:
                                depeartment = 'BOH'
                            if depeartment == '':
                                depeartment = 'INIT'
                    print(employee.name, depeartment)

        #     print(employee_name, "\n", depeartment)
        # print(rows)