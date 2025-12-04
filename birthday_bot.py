import os
from datetime import date

from dotenv import load_dotenv
import requests

from src.db import *

today = date.today()
today_iso = today.isoformat()

load_dotenv()

# GROUPME_BOT_ID_TULSA_MIDTOWN_DIRECTORS = os.getenv('GROUPME_BOT_ID_TULSA_MIDTOWN_DIRECTORS')
GROUPME_BOT_ID_TEST = os.getenv("GROUPME_BOT_ID_TEST")

def birthday_message(employee: Employee):
    return f"BIRTHDAY DETECTED IN HR/PAYROLL\n{employee.name}"

def message_groupme(msg: str, bot_ids: list[str]):
    url = "https://api.groupme.com/v3/bots/post"
    for bot_id in bot_ids:
        payload = {
            "text": msg,
            "bot_id": bot_id 
        }
        try:
            requests.post(url, json=payload).raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send to bot {bot_id}: {e}")


def message_southroads(employee: Employee):
    msg = birthday_message(employee)
    message_groupme(msg, [GROUPME_BOT_ID_TEST])


def message_utica(employee: Employee):
    msg = birthday_message(employee)
    message_groupme(msg, [GROUPME_BOT_ID_TEST])

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
        bday_parts = employee.birthday.split('-')
        if len(bday_parts) != 3:
            continue
        bday_month = bday_parts[1]
        bday_day = bday_parts[2]
        today_parts = today_iso.split('-')
        today_month = today_parts[1]
        today_day = today_parts[2]
        if today_day == bday_day and today_month == bday_month:
            birthday_employees.append([employee, location_number])

for group in birthday_employees:
    employee = group[0]
    location_number = group[1]
    if location_number == 3253:
        message_southroads(employee)
    if location_number == 5429:
        message_utica(employee)
