import json
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO
from urllib.parse import quote

from PyPDF2 import PdfReader


class TimePunchEmployee:
    def __init__(
        self,
        name,
        total_time,
        regular_hours,
        regular_wages,
        overtime_hours,
        overtime_wages,
        total_wages,
    ):
        self.name = name
        self.total_time = total_time
        self.regular_hours = regular_hours
        self.regular_wages = Decimal(regular_wages)
        self.overtime_hours = overtime_hours
        self.overtime_wages = Decimal(overtime_wages)
        self.total_wages = Decimal(total_wages)


class TimePunchReader:
    def __init__(self, time_punch_file: bytes, current_employees: list):
        self.time_punch_bytes = BytesIO(time_punch_file)

        self.current_employees = current_employees
        self.time_punch_employees = []

        self.text = ""

        # Cost buckets
        self.term_cost = Decimal(0)
        self.boh_cost = Decimal(0)
        self.cst_cost = Decimal(0)
        self.rlt_cost = Decimal(0)
        self.foh_cost = Decimal(0)
        self.training_cost = Decimal(0)
        self.executive_cost = Decimal(0)
        self.partner_cost = Decimal(0)

        # Percentage buckets
        self.term_percentage = 0
        self.boh_percentage = 0
        self.cst_percentage = 0
        self.rlt_percentage = 0
        self.foh_percentage = 0
        self.training_percentage = 0
        self.executive_percentage = 0
        self.partner_percentage = 0

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

        lines = self.text.split("\n")
        trim = []
        for line in lines:
            if "," in line:
                if "From " in line:
                    continue
                if "Mon," in line:
                    continue
                if "Tue," in line:
                    continue
                if "Wed," in line:
                    continue
                if "Thu," in line:
                    continue
                if "Fri," in line:
                    continue
                if "Sat," in line:
                    continue
                if "Sun," in line:
                    continue
                if (
                    'Punch types of "Break (Conv to Paid)" were created by Time Punch due to an unpaid break that did not meet the Minimum Unpaid Break Duration setting.'
                    in line
                ):
                    line = line.replace(
                        'Punch types of "Break (Conv to Paid)" were created by Time Punch due to an unpaid break that did not meet the Minimum Unpaid Break Duration setting.',
                        "",
                    )
                    trim.append(line)
                    continue
                trim.append(line)
                continue
            if ":" in line:
                if (
                    'Punch types of "Break (Conv to Paid)" were created by Time Punch due to an unpaid break that did not meet the Minimum Unpaid Break Duration setting.'
                    in line
                ):
                    line = line.replace(
                        'Punch types of "Break (Conv to Paid)" were created by Time Punch due to an unpaid break that did not meet the Minimum Unpaid Break Duration setting.',
                        "",
                    )
                    trim.append(line)
                    continue
                if "AM" in line or "PM" in line or " am " in line or " pm " in line:
                    continue
                trim.append(line)
                continue
        filtered_again = []
        for line in trim:
            if line.startswith("Punch"):
                continue
            filtered_again.append(line)
        grand_total_line = filtered_again.pop()
        names = []
        totals = []
        toggle = 0
        for line in filtered_again:
            if toggle == 0:
                names.append(line)
                toggle = 1
                continue
            if toggle == 1:
                totals.append(line)
                toggle = 0
                continue
        for i, name in enumerate(names):
            total = totals[i]
            total_trimmed = total.replace("Employee Totals ", "")
            parts = total_trimmed.split(" ")
            time_punch_employee = TimePunchEmployee(
                name,
                parts[0],
                parts[1],
                Decimal(parts[2].replace("$", "").replace(",", "")),
                parts[3],
                Decimal(parts[4].replace("$", "").replace(",", "")),
                Decimal(parts[5].replace("$", "").replace(",", "")),
            )
            self.time_punch_employees.append(time_punch_employee)
        grand_total_line = grand_total_line.replace("All Employees Grand Total ", "")
        grand_total_parts = grand_total_line.split(" ")
        self.total_hours = grand_total_parts[0]
        self.regular_hours = grand_total_parts[1]
        self.regular_wages = Decimal(
            grand_total_parts[2].replace("$", "").replace(",", "")
        )
        self.overtime_hours = grand_total_parts[3]
        self.overtime_wages = Decimal(
            grand_total_parts[4].replace("$", "").replace(",", "")
        )
        self.total_wages = Decimal(
            grand_total_parts[5].replace("$", "").replace(",", "")
        )

    def init_department_totals(self):
        for time_punch_employee in self.time_punch_employees:
            found = False
            for current_employee in self.current_employees:
                if time_punch_employee.name == current_employee.time_punch_name:
                    found = True
                    # Check for specific departments (excluding NONE)
                    if current_employee.department == "BOH":
                        self.boh_cost += time_punch_employee.total_wages
                    elif current_employee.department == "FOH":
                        self.foh_cost += time_punch_employee.total_wages
                    elif current_employee.department == "CST":
                        self.cst_cost += time_punch_employee.total_wages
                    elif current_employee.department == "RLT":
                        self.rlt_cost += time_punch_employee.total_wages
                    elif current_employee.department == "TRAINING":
                        self.training_cost += time_punch_employee.total_wages
                    elif current_employee.department == "EXECUTIVE":
                        self.executive_cost += time_punch_employee.total_wages
                    elif current_employee.department == "PARTNER":
                        self.partner_cost += time_punch_employee.total_wages
                    break
            
            # Logic for Terminated/Unmatched employees
            if found == False:
                self.term_cost += time_punch_employee.total_wages

        # Calculate Percentages
        if self.total_wages > 0:
            self.term_percentage = ((self.term_cost * 100) / self.total_wages).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            self.foh_percentage = ((self.foh_cost * 100) / self.total_wages).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            self.rlt_percentage = ((self.rlt_cost * 100) / self.total_wages).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            self.cst_percentage = ((self.cst_cost * 100) / self.total_wages).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            self.boh_percentage = ((self.boh_cost * 100) / self.total_wages).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            self.training_percentage = ((self.training_cost * 100) / self.total_wages).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            self.executive_percentage = ((self.executive_cost * 100) / self.total_wages).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            self.partner_percentage = ((self.partner_cost * 100) / self.total_wages).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

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
            f"  TRAINING: ${self.training_cost} ({self.training_percentage}%)",
            f"  EXECUTIVE: ${self.executive_cost} ({self.executive_percentage}%)",
            f"  PARTNER: ${self.partner_cost} ({self.partner_percentage}%)",
            "",
            "Employees:",
        ]
        return "\n".join(lines)

    def to_json(self):
        dict = {
            "boh_cost": float(self.boh_cost),
            "cst_cost": float(self.cst_cost),
            "rlt_cost": float(self.rlt_cost),
            "foh_cost": float(self.foh_cost),
            "term_cost": float(self.term_cost),
            "training_cost": float(self.training_cost),
            "executive_cost": float(self.executive_cost),
            "partner_cost": float(self.partner_cost),
            
            "boh_percentage": float(self.boh_percentage),
            "cst_percentage": float(self.cst_percentage),
            "rlt_percentage": float(self.rlt_percentage),
            "foh_percentage": float(self.foh_percentage),
            "term_percentage": float(self.term_percentage),
            "training_percentage": float(self.training_percentage),
            "executive_percentage": float(self.executive_percentage),
            "partner_percentage": float(self.partner_percentage),

            "total_hours": str(self.total_hours),
            "regular_hours": str(self.regular_hours),
            "overtime_hours": str(self.overtime_hours),
            "regular_wages": float(self.regular_wages),
            "overtime_wages": float(self.overtime_wages),
            "total_wages": float(self.total_wages),
        }
        json_str = json.dumps(dict)
        safe_json = quote(json_str)
        return safe_json