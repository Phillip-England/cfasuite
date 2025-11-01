from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response

from typing import Optional

from ..middleware import sqlite_connection
from ..config import AppConfig
from ..db import Session

def get_form_logout(app: FastAPI, config: AppConfig):
    @app.get('/form/logout')
    async def get_form_logout(response: Response, session_key: Optional[str] = None):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        if session_key == None:
            return RedirectResponse("/", status_code=303)
        current_session = Session.sqlite_get_by_user_id(c, config.admin_id)
        if current_session == None:
            return RedirectResponse("/", status_code=303)
        if session_key != current_session.key:
            return RedirectResponse("/", status_code=303)
        Session.sqlite_delete_by_session_key(c, session_key)
        conn.commit()
        conn.close()
        response = RedirectResponse(url="/", status_code=303)
        response.delete_cookie("APP_SESSION_ID", httponly=True, secure=True, samesite="lax")
        return response
