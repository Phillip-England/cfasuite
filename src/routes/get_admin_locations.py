from typing import Optional

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse

from ..config import AppConfig
from ..context import depend_context
from ..db import Location
from ..middleware import middleware_auth, sqlite_connection


def get_admin_locations(app: FastAPI, config: AppConfig):
    @app.get("/admin/cfa_locations")
    async def get_admin_locations(
        request: Request,
        err_create_location: Optional[str] = "",
        context=Depends(depend_context),
    ):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None:
            return RedirectResponse("/", 303)
        cfa_locations = Location.sqlite_find_all(c)
        conn.close()
        return context["templates"].TemplateResponse(
            request,
            "page/admin/locations.html",
            {
                "cfa_locations": cfa_locations,
                "err_create_location": err_create_location,
                "session_key": session.key,
            },
        )
