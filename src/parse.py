from PyPDF2 import PdfReader

from decimal import Decimal, ROUND_HALF_UP

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
    def __init__(self, time_punch_bytes: bytes, current_employees: list):
        self.time_punch_bytes = time_punch_bytes

        self.current_employees = current_employees
        self.time_punch_employees = []

        self.raw_data = time_punch_bytes
        self.text = ''

        self.boh_cost = Decimal(0)
        self.cst_cost = Decimal(0)
        self.rlt_cost = Decimal(0)
        self.foh_cost = Decimal(0)

        self.boh_percentage = 0
        self.cst_percentage = 0
        self.rlt_percentage = 0
        self.foh_percentage = 0

        self.total_hours = 0
        self.regular_hours = 0
        self.overtime_hours = 0

        self.regular_wages = Decimal(0)
        self.overtime_wages = Decimal(0)
        self.total_wages = Decimal(0)

        self.init_pdf_totals()
        self.init_department_totals()

    def init_pdf_totals(self):
        reader = PdfReader(self.time_punch_bytes)
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
            time_punch_employee = TimePunchEmployee(name, parts[0], parts[1], Decimal(parts[2].replace('$', '').replace(',', '')), parts[3], Decimal(parts[4].replace('$', '').replace(',', '')), Decimal(parts[5].replace('$', '').replace(',', '')))
            self.time_punch_employees.append(time_punch_employee)
        grand_total_line = grand_total_line.replace('All Employees Grand Total ', '')
        grand_total_parts = grand_total_line.split(' ')
        self.total_hours = grand_total_parts[0]
        self.regular_hours = grand_total_parts[1]
        self.regular_wages = Decimal(grand_total_parts[2].replace('$', '').replace(',', ''))
        self.overtime_hours = grand_total_parts[3]
        self.overtime_wages = Decimal(grand_total_parts[4].replace('$', '').replace(',', ''))
        self.total_wages = Decimal(grand_total_parts[5].replace('$', '').replace(',', ''))

    def init_department_totals(self):
        for time_punch_employee in self.time_punch_employees:
            for current_employee in self.current_employees:
                if time_punch_employee.name == current_employee.time_punch_name:
                    if current_employee.department == 'BOH':
                        self.boh_cost += time_punch_employee.total_wages
                    if current_employee.department == 'FOH':
                        self.foh_cost += time_punch_employee.total_wages
                    if current_employee.department == 'CST':
                        self.cst_cost += time_punch_employee.total_wages
                    if current_employee.department == 'RLT':
                        self.rlt_cost += time_punch_employee.total_wages
                    break
        self.foh_percentage = ((self.foh_cost*100)/self.total_wages).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.rlt_percentage = ((self.rlt_cost*100)/self.total_wages).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.cst_percentage = ((self.cst_cost*100)/self.total_wages).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.boh_percentage = ((self.boh_cost*100)/self.total_wages).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        lines = [
            f"Total Hours: {self.total_hours}",
            f"Regular Hours: {self.regular_hours}, Regular Wages: ${self.regular_wages}",
            f"Overtime Hours: {self.overtime_hours}, Overtime Wages: ${self.overtime_wages}",
            f"Total Wages: ${self.total_wages}",
            "",
            "Department Costs:",
            f"  BOH: ${self.boh_cost} ({self.boh_percentage}%)",
            f"  FOH: ${self.foh_cost} ({self.foh_percentage}%)",
            f"  CST: ${self.cst_cost} ({self.cst_percentage}%)",
            f"  RLT: ${self.rlt_cost} ({self.rlt_percentage}%)",
            "",
            "Employees:"
        ]
        return "\n".join(lines)
