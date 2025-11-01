import json

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse

from typing import Optional

from ..middleware import sqlite_connection, middleware_auth
from ..context import depend_context
from ..config import AppConfig
from ..db import Location, Employee

def get_admin_cfa_location(app: FastAPI, config: AppConfig):
    @app.get("/admin/cfa_location/{location_id}")
    async def get_admin_cfa_location(
        request: Request,
        location_id: int,
        time_punch_json: Optional[str] = None,
        context=Depends(depend_context),
    ):
        time_punch_data = None
        if time_punch_json:
            time_punch_data = json.loads(time_punch_json)
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None:
            return RedirectResponse("/", 303)
        cfa_location = Location.sqlite_find_by_id(c, location_id)
        employees = Employee.sqlite_find_all_by_cfa_location_id(c, cfa_location.id)
        conn.close()
        return context["templates"].TemplateResponse(
            request,
            "page/admin/location.html",
            context={
                "cfa_location": cfa_location,
                "employees": employees,
                "session_key": session.key,
                "time_punch_data": time_punch_data,
            },
        )