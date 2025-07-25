from typing import Annotated, Optional

from fastapi import Request, Depends
from fastapi.responses import RedirectResponse

from src.db import *
from src.middleware import *
from src.server import *

async def get_admin(
    request: Request, 
    context = Depends(depend_context)
):
    conn = sqlite_connection()
    c = conn.cursor()
    admin_user_id = os.getenv('ADMIN_USER_ID')
    session = middleware_auth(c, request, admin_user_id)
    if session == None:
        return RedirectResponse('/', 303)
    conn.close()
    return context['templates'].TemplateResponse(request, "page/admin/home.html", {
        'session_key': session.key,
    })


async def get_app_locations(
    request: Request,
    err_create_location: Optional[str] = '',
    context = Depends(depend_context)
):
    conn = sqlite_connection()
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None:
        return RedirectResponse('/', 303)
    cfa_locations = DataCfaLocation.sqlite_find_all(c)
    conn.close()
    return context['templates'].TemplateResponse(request, "page/admin/cfa_locations.html", {
            "id": id, 
            "cfa_locations": cfa_locations,
            'err_create_location': err_create_location,
            'session_key': session.key,
        }
    )


async def get_app_cfa_location(
    request: Request, 
    location_id: int,
    time_punch_json: Optional[str] = None,    
    context = Depends(depend_context)
):
    time_punch_data = None
    if time_punch_json:
        time_punch_data = json.loads(time_punch_json)
    conn = sqlite_connection()
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None:
        return RedirectResponse('/', 303)
    cfa_location = DataCfaLocation.sqlite_find_by_id(c, location_id)
    employees = DataEmployee.sqlite_find_all_by_cfa_location_id(c, cfa_location.id)
    conn.close()
    return context['templates'].TemplateResponse(request, 'page/admin/cfa_location.html', context={''
        'cfa_location': cfa_location, 
        'employees': employees,
        'session_key': session.key,
        'time_punch_data': time_punch_data,
    })