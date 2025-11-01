from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse


from ..middleware import sqlite_connection, middleware_auth
from ..context import depend_context
from ..config import AppConfig


def get_admin(app: FastAPI, config: AppConfig):
    @app.get("/admin")
    async def get_admin(request: Request, context=Depends(depend_context)):
        conn, c = sqlite_connection(config.sqlite_absolute_path)
        session = middleware_auth(c, request, config.admin_id)
        if session == None:
            return RedirectResponse("/", 303)
        conn.close()
        return context["templates"].TemplateResponse(
            request,
            "page/admin/home.html",
            {
                "session_key": session.key,
            },
        )
