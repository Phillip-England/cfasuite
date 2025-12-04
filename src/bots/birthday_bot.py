import os
from datetime import date
import requests
from dotenv import load_dotenv

from src.db import *

load_dotenv()

# --- Configuration & Env Vars ---
GROUPME_BOT_ID_MIDTOWN_TULSA_DIRECTORS = os.getenv('GROUPME_BOT_ID_MIDTOWN_TULSA_DIRECTORS')
GROUPME_BOT_ID_MIDTOWN_LEADERSHIP = os.getenv("GROUPME_BOT_ID_MIDTOWN_LEADERSHIP")
SQLITE_ABSOLUTE_PATH = os.getenv("SQLITE_ABSOLUTE_PATH")

# --- Helper Functions ---

def birthday_message(employee: Employee):
    return f"BIRTHDAY DETECTED IN HR/PAYROLL\n{employee.name}"

def message_groupme(employee: Employee):
    """
    Sends a birthday message to the default leadership/director bots.
    """
    msg = birthday_message(employee)
    bot_ids = [
        GROUPME_BOT_ID_MIDTOWN_TULSA_DIRECTORS,
        GROUPME_BOT_ID_MIDTOWN_LEADERSHIP,
    ]
    url = "https://api.groupme.com/v3/bots/post"
    
    for bot_id in bot_ids:
        # Skip if env var is missing
        if not bot_id:
            continue
            
        payload = {
            "text": msg,
            "bot_id": bot_id 
        }
        try:
            requests.post(url, json=payload).raise_for_status()
            print(f"Sent birthday message for {employee.name} to bot {bot_id}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send to bot {bot_id}: {e}")

# --- Main Logic Function ---

def process_daily_birthdays():
    """
    Connects to the DB, finds employees with birthdays today, 
    and sends GroupMe messages based on location.
    """
    # 1. Setup Date
    today = date.today()
    today_iso = today.isoformat()
    today_parts = today_iso.split('-')
    today_month = today_parts[1]
    today_day = today_parts[2]

    # 2. Database Connection
    if not SQLITE_ABSOLUTE_PATH:
        print("Error: SQLITE_ABSOLUTE_PATH not set in environment.")
        return

    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    
    location_numbers = [3253, 5429]
    birthday_employees = []

    print(f"Checking for birthdays on {today_iso}...")

    # 3. Find Birthday Employees
    for location_number in location_numbers:
        location = Location.sqlite_find_by_number(c, location_number)
        if location is None:
            continue
            
        employees = Employee.sqlite_find_all_by_cfa_location_id(c, location.id)
        
        for employee in employees:
            if not employee.birthday:
                continue
                
            bday_parts = employee.birthday.split('-')
            if len(bday_parts) != 3:
                continue
            
            bday_month = bday_parts[1]
            bday_day = bday_parts[2]
            
            if today_day == bday_day and today_month == bday_month:
                birthday_employees.append([employee, location_number])

    # 4. Send Messages
    if not birthday_employees:
        print("No birthdays found today.")
    
    messaged_names = []

    for group in birthday_employees:
        employee = group[0]
        location_number = group[1]

        if employee.name in messaged_names:
            continue
        messaged_names.append(employee.name)

        message_groupme(employee)
            
    # Close connection (Good practice)
    conn.close()