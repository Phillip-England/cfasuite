from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse

from ..middleware import sqlite_connection, middleware_auth
from ..config import AppConfig
from ..db import Location

def post_form_cfa_location_delete(app: FastAPI, config: AppConfig):
    @app.post('/form/cfa_location/delete/{id}')
    async def post_form_cfa_location_delete(
        request: Request,
        id: int,
        cfa_location_number: int | None = Form(None),
        session_key: str | None = Form(None),
    ):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None or session_key != session.key:
            return RedirectResponse("/", 303)
        cfa_location = Location.sqlite_find_by_id(c, id)
        if cfa_location == None:
            return JSONResponse({"message": "unauthorized"}, 401)
        if cfa_location.number != cfa_location_number:
            return JSONResponse({"message": "unauthorized"}, 401)
        Location.sqlite_delete_by_id(c, id)
        conn.commit()
        conn.close()
        return RedirectResponse("/admin/cfa_locations", 303)

