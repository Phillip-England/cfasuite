from fastapi import UploadFile
from pandas import read_excel
from io import BytesIO

class EmployeeBirthdayReader:
    def __init__(self, birthday_dict: dict):
        self.birthday_dict = birthday_dict
        return

    @staticmethod
    async def new(file: UploadFile):
        birthday_dict = {}
        file_contents = await file.read()
        df = read_excel(BytesIO(file_contents))
        for i, row in df.iterrows():
            name = row['Employee Name']
            bday = row['Birth Date']
            bday_parts = bday.split('/')
            bday_final = f'{bday_parts[2]}-{bday_parts[1]}-{bday_parts[0]}'
            birthday_dict[name] = bday_final
            # employee_status = row["Employee Status"]
            # if employee_status == "Terminated":
            #     continue
            # name = row["Employee Name"]
            # names.append(name)
        return EmployeeBirthdayReader(birthday_dict)


