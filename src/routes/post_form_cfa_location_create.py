from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse

from ..config import AppConfig
from ..db import Location
from ..middleware import middleware_auth, sqlite_connection


def post_form_cfa_location_create(app: FastAPI, config: AppConfig):
    @app.post("/form/cfa_location/create")
    async def post_form_cfa_location_create(
        request: Request,
        name: str | None = Form(None),
        number: str | None = Form(None),
        session_key: str | None = Form(None),
    ):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None or session_key != session.key:
            return RedirectResponse("/", 303)
        potential_location = Location.sqlite_find_by_number(c, number)
        if potential_location != None:
            return RedirectResponse(
                "/admin/cfa_locations?err_create_location=location with provided number already exists",
                303,
            )
        Location.sqlite_insert_one(c, name, number)
        conn.commit()
        conn.close()
        return RedirectResponse(url="/admin/cfa_locations", status_code=303)
