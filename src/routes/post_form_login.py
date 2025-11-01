from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, Response

from ..middleware import sqlite_connection
from ..config import AppConfig
from ..db import Session

def post_form_login(app: FastAPI, config: AppConfig):
    @app.post("/form/login")
    async def post_form_login(
        response: Response,
        username: str | None = Form(None),
        password: str | None = Form(None),
    ):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        if username != config.admin_username or password != config.admin_password:
            conn.close()
            return RedirectResponse(url="/", status_code=303)
        pre_existing_session = Session.sqlite_get_by_user_id(c, config.admin_id)
        if pre_existing_session != None:
            Session.sqlite_delete_by_id(c, pre_existing_session.id)
        print(config.admin_id)
        session = Session.sqlite_insert(c, config.admin_id)
        conn.commit()
        conn.close()
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(
            "APP_SESSION_ID",
            session.id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800,
        )
        return response
