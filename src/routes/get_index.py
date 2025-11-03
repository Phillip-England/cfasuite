from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse

from src import *

from ..config import AppConfig
from ..context import depend_context
from ..db import Session
from ..middleware import sqlite_connection


def get_index(app: FastAPI, config: AppConfig):
    @app.get("/")
    async def get_index(request: Request, context=Depends(depend_context)):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session_id = request.cookies.get("APP_SESSION_ID")
        session = Session.sqlite_get_by_id(c, session_id)
        if session != None:
            if int(session.user_id) == int(config.admin_id):
                conn.close()
                return RedirectResponse("/admin", status_code=303)
        conn.close()
        return context["templates"].TemplateResponse(
            request, "page/guest/home.html", {}
        )
