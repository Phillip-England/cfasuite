from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import RedirectResponse
from pandas import read_excel

from typing import Annotated

from ..config import AppConfig
from ..middleware import middleware_auth, sqlite_connection
from ..parse import HotSchedulesStaffReader
from ..db import Employee

def post_form_upload_hotschedules_staff_html(app: FastAPI, config: AppConfig):
    @app.post('/form/upload/hotschedules_staff_html')
    async def post_form_upload_hotschedules_staff_html(
        request: Request,
        cfa_location_id: str | None = Form(None),
        html: str | None = Form(None)
    ):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None:
            return RedirectResponse("/", 303)
        employees = Employee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)
        
        reader = await HotSchedulesStaffReader.new(html)
        return RedirectResponse(
            url=f"/admin/cfa_location/{cfa_location_id}", status_code=303
        )