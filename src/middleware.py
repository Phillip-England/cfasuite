from fastapi import Request

from src.db import *


def middleware_auth(c: Cursor, request: Request, user_id: str):
    session_id = request.cookies.get('APP_SESSION_ID')
    if session_id == None:
        return None
    session = DataSession.sqlite_get_by_id(c, session_id)
    if session == None:
        return None
    if str(session.user_id) != str(user_id):
        return None
    return session