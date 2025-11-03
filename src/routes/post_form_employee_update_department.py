from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse

from ..config import AppConfig
from ..db import Employee
from ..middleware import middleware_auth, sqlite_connection


def post_form_employee_update_department(app: FastAPI, config: AppConfig):
    @app.post("/form/employee/update/department")
    async def post_form_employee_update_department(
        request: Request,
        department: str | None = Form(None),
        employee_id: str | None = Form(None),
        location_id: str | None = Form(None),
        session_key: str | None = Form(None),
    ):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None or session_key != session.key:
            return RedirectResponse("/", 303)
        Employee.sqlite_update_department(c, employee_id, department)
        conn.commit()
        conn.close()
        return RedirectResponse(f"/admin/cfa_location/{location_id}", 303)
