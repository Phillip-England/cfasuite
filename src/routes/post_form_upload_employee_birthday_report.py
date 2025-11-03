from typing import Annotated

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse

from ..config import AppConfig
from ..db import Employee
from ..middleware import middleware_auth, sqlite_connection
from ..parse import EmployeeBirthdayReader


def post_form_upload_employee_birthday_report(app: FastAPI, config: AppConfig):
    @app.post("/form/upload/employee_birthday_report")
    async def post_form_employee_bio(
        request: Request,
        file: Annotated[UploadFile, File()],
        cfa_location_id: str | None = Form(None),
    ):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None:
            return RedirectResponse("/", 303)
        employees = Employee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)
        reader = await EmployeeBirthdayReader.new(file)
        for name in reader.birthday_dict:
            bday = reader.birthday_dict[name]
            for employee in employees:
                if employee.time_punch_name == name:
                    Employee.sqlite_add_birthday(c, employee.id, bday)
                    break
        conn.commit()
        conn.close()
        return RedirectResponse(
            url=f"/admin/cfa_location/{cfa_location_id}", status_code=303
        )
