from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import RedirectResponse

from typing import Annotated

from ..middleware import sqlite_connection, middleware_auth
from ..config import AppConfig
from ..parse import EmployeeBioReader

def post_form_upload_employee_bio(app: FastAPI, config: AppConfig):
    @app.post("/form/upload/employee_bio")
    async def post_form_upload_employee_bio(
        request: Request,
        file: Annotated[UploadFile, File()], cfa_location_id: str | None = Form(None)
    ):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None:
            return RedirectResponse("/", 303)
        reader = await EmployeeBioReader.new(file)
        reader.insert_all_employees(conn, c, cfa_location_id)
        reader.remove_terminated_employees(conn, c, cfa_location_id)
        conn.commit()
        conn.close()
        return RedirectResponse(
            url=f"/admin/cfa_location/{cfa_location_id}", status_code=303
        )