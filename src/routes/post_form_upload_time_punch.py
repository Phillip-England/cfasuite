from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import RedirectResponse

from typing import Annotated

from ..middleware import sqlite_connection, middleware_auth
from ..config import AppConfig
from ..db import Employee
from ..parse import TimePunchReader

def post_form_upload_time_punch(app: FastAPI, config: AppConfig):
    @app.post('/post/form/upload/time_punch')
    async def post_form_upload_time_punch(
        request: Request,
        file: Annotated[UploadFile, File()],
        cfa_location_id: str | None = Form(None),
        session_key: str | None = Form(None),
    ):
        try:
            contents = await file.read()
            conn, c = sqlite_connection(config.sqlite_absolute_path)
            session = middleware_auth(c, request, config.admin_id)
            if session == None or session_key != session.key:
                return RedirectResponse("/", 303)
            current_employees = Employee.sqlite_find_all_by_cfa_location_id(
                c, cfa_location_id
            )
            time_punch_pdf = TimePunchReader(contents, current_employees)
            conn.close()
            return RedirectResponse(
                url=f"/admin/cfa_location/{cfa_location_id}?time_punch_json={time_punch_pdf.to_json()}",
                status_code=303,
            )
        except Exception as e:
            return {"message": str(e)}