from bs4 import BeautifulSoup
from sqlite3 import Cursor

from io import BytesIO

class HotSchedulesStaffReader:
    def __init__(self):
        return
    
    @staticmethod
    async def new(html: str):
        soup = BeautifulSoup(html, 'html.parser')
        staff_table = soup.find(id='stafftable')
        rows = staff_table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 7:
                continue
            employee_name = cols[1].text
            employee_jobs = cols[6]
            depeartment = ''
            if employee_jobs.text == '-':
                depeartment = 'NONE'

            print(employee_name, "\n", depeartment)
        # print(rows)