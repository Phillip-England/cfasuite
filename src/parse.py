from io import BytesIO

from pdfminer.high_level import extract_text
from PyPDF2 import PdfReader
import fitz

from pandas import DataFrame

from src.log import logi, logi_append

class EmployeeBioReader:
    def __init__(self, df: DataFrame):
        self.names = []
        for i, row in df.iterrows():
            employee_status = row["Employee Status"]
            if employee_status == "Terminated":
                continue
            name = row["Employee Name"]
            self.names.append(name)

class TimePunchEmployee:
    def __init__(self, name, total_time, regular_hours, regular_wages, overtime_hours, overtime_wages, total_wages):
        self.name = name
        self.total_time = total_time
        self.regular_hours = regular_hours
        self.regular_wages = regular_wages
        self.overtime_hours = overtime_hours
        self.overtime_wages = overtime_wages
        self.total_wages = total_wages


class TimePunchReader:
    def __init__(self, time_punch_bytes: bytes):
        self.time_punch_employees = []
        self.raw_data = time_punch_bytes
        self.text = ''
        reader = PdfReader(time_punch_bytes)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                self.text += page_text

        lines = self.text.split('\n')
        trim = []
        for line in lines:
            if ',' in line: 
                if 'From ' in line:
                    continue
                if 'Mon,' in line:
                    continue
                if 'Tue,' in line:
                    continue
                if 'Wed,' in line:
                    continue
                if 'Thu,' in line:
                    continue
                if 'Fri,' in line:
                    continue
                if 'Sat,' in line:
                    continue
                if 'Sun,' in line:
                    continue
                trim.append(line)
                continue
            if ':' in line:
                if 'Punch types of "Break (Conv to Paid)" were created by Time Punch due to an unpaid break that did not meet the Minimum Unpaid Break Duration setting.' in line:
                    line = line.replace('Punch types of "Break (Conv to Paid)" were created by Time Punch due to an unpaid break that did not meet the Minimum Unpaid Break Duration setting.', '')
                    trim.append(line)
                    continue
                if 'AM' in line or 'PM' in line or ' am ' in line or ' pm ' in line:
                    continue
                trim.append(line)
                continue
        grand_total_line = trim.pop()
        names = []
        totals = []
        toggle = 0
        for line in trim:
            if toggle == 0:
                names.append(line)
                toggle = 1
                continue
            if toggle == 1:
                totals.append(line)
                toggle = 0
                continue
        for (i, name) in enumerate(names):
            total = totals[i]
            total_trimmed = total.replace('Employee Totals ', '')
            parts = total_trimmed.split(' ')
            time_punch_employee = TimePunchEmployee(name, parts[0], parts[1], float(parts[2].replace('$', '').replace(',', '')), parts[3], float(parts[4].replace('$', '').replace(',', '')), float(parts[5].replace('$', '').replace(',', '')))
            self.time_punch_employees.append(time_punch_employee)
        grand_total_line = grand_total_line.replace('All Employees Grand Total ', '')
        grand_total_parts = grand_total_line.split(' ')
        self.total_time = grand_total_parts[0]
        self.regular_hours = grand_total_parts[1]
        self.regular_wages = float(grand_total_parts[2].replace('$', '').replace(',', ''))
        self.overtime_hours = grand_total_parts[3]
        self.overtime_wages = float(grand_total_parts[4].replace('$', '').replace(',', ''))
        self.total_wages = float(grand_total_parts[5].replace('$', '').replace(',', ''))