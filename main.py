import os

from io import BytesIO

import json

from typing import Annotated, Optional

from fastapi import FastAPI, Request, UploadFile, File, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pandas import read_excel

from dotenv import load_dotenv

from src.db import *
from src.parse import *
from src.log import *

load_dotenv()
logi_clear()

sqlite_path = './main.db'
init_conn = sqlite_connection(sqlite_path)
init_cursor = init_conn.cursor()
DataCfaLocation.sqlite_create_table(init_cursor)
DataEmployee.sqlite_create_table(init_cursor)
DataSession.sqlite_create_table(init_cursor)
init_conn.commit()
init_conn.close()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
t = Jinja2Templates(directory="templates")

@app.get('/', response_class=HTMLResponse)
async def get_index(request: Request):
    return t.TemplateResponse(request, 'page/guest/home.html', {}
    )

@app.get("/admin", response_class=HTMLResponse)
async def read_item(request: Request):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None:
        return RedirectResponse('/', 303)
    conn.close()
    return t.TemplateResponse(request, "page/admin/home.html", {
        'session_key': session.key,
    })

@app.get("/admin/cfa_locations", response_class=HTMLResponse)
async def get_app_locations(
    request: Request,
    err_create_location: Optional[str] = ''
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None:
        return RedirectResponse('/', 303)
    cfa_locations = DataCfaLocation.sqlite_find_all(c)
    conn.close()
    return t.TemplateResponse(request, "page/admin/cfa_locations.html", {
            "id": id, 
            "cfa_locations": cfa_locations,
            'err_create_location': err_create_location,
            'session_key': session.key,
        }
    )

@app.get('/admin/cfa_location/{location_id}')
async def get_app_cfa_location(
    request: Request, 
    location_id: int,
    time_punch_json: Optional[str] = None,    
):
    time_punch_data = None
    if time_punch_json:
        time_punch_data = json.loads(time_punch_json)
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None:
        return RedirectResponse('/', 303)
    cfa_location = DataCfaLocation.sqlite_find_by_id(c, location_id)
    employees = DataEmployee.sqlite_find_all_by_cfa_location_id(c, cfa_location.id)
    conn.close()
    return t.TemplateResponse(request, 'page/admin/cfa_location.html', context={''
        'cfa_location': cfa_location, 
        'employees': employees,
        'session_key': session.key,
        'time_punch_data': time_punch_data,
    })

@app.post('/form/login')
async def post_login(
    response: Response,
    username: str | None = Form(None),
    password: str | None = Form(None),
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
        admin_id = os.getenv('ADMIN_USER_ID')
        potential_session = DataSession.sqlite_get_by_user_id(c, admin_id)
        if potential_session != None:
            DataSession.sqlite_delete_by_id(c, potential_session.id)
        session = DataSession.sqlite_insert(c, admin_id)
        conn.commit()
        conn.close()
        response = RedirectResponse(url='/admin', status_code=303)
        response.set_cookie('APP_SESSION_ID', session.id, httponly=True, secure=True, samesite='strict', max_age=1800)
        return response
    conn.close()
    return RedirectResponse(url='/', status_code=303)

@app.post("/form/upload/employee_bio")
async def post_form_employees_create(
    file: Annotated[UploadFile, File()],
    cfa_location_id: str | None = Form(None)
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    contents = await file.read()
    df = read_excel(BytesIO(contents))
    reader = EmployeeBioReader(df)
    current_employees = DataEmployee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)
    reader_names = reader.names
    for name in reader_names:
        found = False
        for employee in current_employees:
            if name == employee.time_punch_name:
                found = True
                break
        if found == False:
            DataEmployee.sqlite_insert_one(c, name, 'INIT', cfa_location_id) 
    conn.commit()
    current_employees = DataEmployee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)          
    for employee in current_employees:
        found = False
        for name in reader_names:
            if name == employee.time_punch_name:
                found = True
                break
        if found == False:
            DataEmployee.sqlite_delete_by_id(c, employee.id) 
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/admin/cfa_location/{cfa_location_id}", status_code=303)

@app.post('/form/cfa_location/create')
async def post_form_cfa_location_create(
    request: Request,
    name: str | None = Form(None), 
    number:str | None = Form(None),
    session_key:str | None = Form(None),
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    potential_location = DataCfaLocation.sqlite_find_by_number(c, number)
    if potential_location != None:
        return RedirectResponse('/admin/cfa_locations?err_create_location=location with provided number already exists', 303)
    DataCfaLocation.sqlite_insert_one(c, name, number)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/cfa_locations", status_code=303)

@app.post('/form/cfa_location/delete/{id}')
async def post_form_cfa_location_delete(
    request: Request,
    id: int,
    cfa_location_number: int | None = Form(None),
    session_key:str | None = Form(None),
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    cfa_location = DataCfaLocation.sqlite_find_by_id(c, id)
    if cfa_location == None:
        return JSONResponse({'message': 'unauthorized'}, 401)
    if cfa_location.number != cfa_location_number:
        return JSONResponse({'message': 'unauthorized'}, 401)
    DataCfaLocation.sqlite_delete_by_id(c, id)
    conn.commit()
    conn.close()
    return RedirectResponse('/admin/cfa_locations', 303)

@app.post('/form/employee/update/department')
async def post_form_employee_update_department(
    request: Request,
    department: str | None = Form(None),
    employee_id: str | None = Form(None),
    location_id: str | None = Form(None),
    session_key:str | None = Form(None),
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    DataEmployee.sqlite_update_department(c, employee_id, department)
    conn.commit()
    conn.close()
    return RedirectResponse(f'/admin/cfa_location/{location_id}', 303)
    
@app.post("/form/upload/time_punch")
async def post_form_employees_create(
    request: Request,
    file: Annotated[UploadFile, File()],
    cfa_location_id: str | None = Form(None),
    session_key:str | None = Form(None),
):
    contents = await file.read()
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    session = middleware_auth(c, request, os.getenv('ADMIN_USER_ID'))
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    current_employees = DataEmployee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)
    time_punch_pdf = TimePunchReader(contents, current_employees)
    logi(time_punch_pdf.__str__())
    conn.close()
    return RedirectResponse(url=f"/admin/cfa_location/{cfa_location_id}?time_punch_json={time_punch_pdf.to_json()}", status_code=303)

def middleware_auth(c: Cursor, request: Request, user_id: str):
    session_id = request.cookies.get('APP_SESSION_ID')
    if session_id == None:
        return None
    session = DataSession.sqlite_get_by_id(c, session_id)
    if session == None:
        return None
    if session.user_id != user_id:
        return None
    return session