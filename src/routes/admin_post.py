from typing import Annotated
from io import BytesIO

from fastapi import UploadFile, File, Form, Response, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pandas import read_excel

from src.db import *
from src.parse import *
from src.middleware import *

async def post_form_login(
    response: Response,
    username: str | None = Form(None),
    password: str | None = Form(None),
):
    conn = sqlite_connection()
    c = conn.cursor()
    if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
        admin_id = os.getenv('ADMIN_USER_ID')
        potential_session = Session.sqlite_get_by_user_id(c, admin_id)
        if potential_session != None:
            Session.sqlite_delete_by_id(c, potential_session.id)
        session = Session.sqlite_insert(c, admin_id)
        conn.commit()
        conn.close()
        response = RedirectResponse(url='/admin', status_code=303)
        response.set_cookie('APP_SESSION_ID', session.id, httponly=True, secure=True, samesite='lax', max_age=1800)
        return response
    conn.close()
    return RedirectResponse(url='/', status_code=303)


async def post_form_employee_bio(
    file: Annotated[UploadFile, File()],
    cfa_location_id: str | None = Form(None)
):
    conn = sqlite_connection()
    c = conn.cursor()
    contents = await file.read()
    df = read_excel(BytesIO(contents))
    reader = EmployeeBioReader(df)
    current_employees = Employee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)
    reader_names = reader.names
    for name in reader_names:
        found = False
        for employee in current_employees:
            if name == employee.time_punch_name:
                found = True
                break
        if found == False:
            Employee.sqlite_insert_one(c, name, 'INIT', cfa_location_id) 
    conn.commit()
    current_employees = Employee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)          
    for employee in current_employees:
        found = False
        for name in reader_names:
            if name == employee.time_punch_name:
                found = True
                break
        if found == False:
            Employee.sqlite_delete_by_id(c, employee.id) 
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/admin/cfa_location/{cfa_location_id}", status_code=303)

async def post_form_cfa_location_create(
    request: Request,
    name: str | None = Form(None), 
    number:str | None = Form(None),
    session_key:str | None = Form(None),
):
    conn = sqlite_connection()
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    potential_location = Location.sqlite_find_by_number(c, number)
    if potential_location != None:
        return RedirectResponse('/admin/cfa_locations?err_create_location=location with provided number already exists', 303)
    Location.sqlite_insert_one(c, name, number)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/cfa_locations", status_code=303)


async def post_form_cfa_location_delete(
    request: Request,
    id: int,
    cfa_location_number: int | None = Form(None),
    session_key:str | None = Form(None),
):
    conn = sqlite_connection()
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    cfa_location = Location.sqlite_find_by_id(c, id)
    if cfa_location == None:
        return JSONResponse({'message': 'unauthorized'}, 401)
    if cfa_location.number != cfa_location_number:
        return JSONResponse({'message': 'unauthorized'}, 401)
    Location.sqlite_delete_by_id(c, id)
    conn.commit()
    conn.close()
    return RedirectResponse('/admin/cfa_locations', 303)

async def post_form_employee_update_department(
    request: Request,
    department: str | None = Form(None),
    employee_id: str | None = Form(None),
    location_id: str | None = Form(None),
    session_key:str | None = Form(None),
):
    conn = sqlite_connection()
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    Employee.sqlite_update_department(c, employee_id, department)
    conn.commit()
    conn.close()
    return RedirectResponse(f'/admin/cfa_location/{location_id}', 303)

async def post_form_upload_time_punch(
    request: Request,
    file: Annotated[UploadFile, File()],
    cfa_location_id: str | None = Form(None),
    session_key:str | None = Form(None),
):
    try:
        contents = await file.read()
        conn = sqlite_connection()
        c = conn.cursor()
        session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
        if session == None or session_key != session.key:
            return RedirectResponse('/', 303)
        current_employees = Employee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)
        time_punch_pdf = TimePunchReader(contents, current_employees)
        conn.close()
        return RedirectResponse(url=f"/admin/cfa_location/{cfa_location_id}?time_punch_json={time_punch_pdf.to_json()}", status_code=303)
    except Exception as e:
        return {"message": str(e)}