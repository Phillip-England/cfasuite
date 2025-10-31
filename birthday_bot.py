import os
from datetime import date

from dotenv import load_dotenv
from src.db import *

today = date.today()
today_iso = today.isoformat()

load_dotenv()

SQLITE_ABSOLUTE_PATH = os.getenv("SQLITE_ABSOLUTE_PATH")
conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
location_numbers = [3253, 5429]
birthday_employees = []
for location_number in location_numbers:
    location = Location.sqlite_find_by_number(c, location_number)
    if location == None:
        continue
    employees = Employee.sqlite_find_all_by_cfa_location_id(c, location.id)
    for employee in employees:
        if employee.birthday == today_iso or employee.birthday == '1993-07-20':
            birthday_employees.append([employee, location_number])

for group in birthday_employees:
    employee = group[0]
    location_number = group[1]
    print(employee.time_punch_name, location_number)

def message_southroads():
    print('southroads')

def message_utica():
    print('utica')