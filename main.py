import os
import json
from io import BytesIO
from typing import Annotated, Optional

from fastapi import FastAPI, Depends, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from pandas import read_excel

from src.db import *
from src.parse import *
from src.log import *
from src.middleware import *
from src.server import *

load_dotenv()

ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
SQLITE_ABSOLUTE_PATH = os.getenv('SQLITE_ABSOLUTE_PATH')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

if ADMIN_USER_ID == None or SQLITE_ABSOLUTE_PATH == None or ADMIN_USERNAME == None or ADMIN_PASSWORD == None:
    print('please configure your .env file before serving cfasuite')
    print('checkout https://github.com/phillip-england/cfasuite for more information')

init_tables(SQLITE_ABSOLUTE_PATH)

app = FastAPI(dependencies=[Depends(depend_context)])
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"Oops! Something went wrong: {exc}"}
    )

@app.get('/')
async def get_index(
    request: Request,
    context = Depends(depend_context)
):
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    session_id = request.cookies.get('APP_SESSION_ID')
    session = Session.sqlite_get_by_id(c, session_id)
    if session != None:
        if int(session.user_id) == int(ADMIN_USER_ID):
            conn.close()
            return RedirectResponse('/admin', status_code=303)
    conn.close()
    return context['templates'].TemplateResponse(request, 'page/guest/home.html', {})

@app.post('/form/login')
async def post_form_login(
    response: Response,
    username: str | None = Form(None),
    password: str | None = Form(None),
):
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        conn.close()
        return RedirectResponse(url='/', status_code=303)
    pre_existing_session = Session.sqlite_get_by_user_id(c, ADMIN_USER_ID)
    if pre_existing_session != None:
        Session.sqlite_delete_by_id(c, pre_existing_session.id)
    session = Session.sqlite_insert(c, ADMIN_USER_ID)
    conn.commit()
    conn.close()
    response = RedirectResponse(url='/admin', status_code=303)
    response.set_cookie('APP_SESSION_ID', session.id, httponly=True, secure=True, samesite='lax', max_age=1800)
    return response

@app.get('/admin')
async def get_admin(
    request: Request,
    context = Depends(depend_context)
):
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    session = middleware_auth(c, request, ADMIN_USER_ID)
    if session == None:
        return RedirectResponse('/', 303)
    conn.close()
    return context['templates'].TemplateResponse(request, "page/admin/home.html", {
        'session_key': session.key,
    })

@app.get('/admin/cfa_locations')
async def get_admin_locations(
    request: Request,
    err_create_location: Optional[str] = '',
    context = Depends(depend_context),
):
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    session = middleware_auth(c, request, ADMIN_USER_ID)
    if session == None:
        return RedirectResponse('/', 303)
    cfa_locations = Location.sqlite_find_all(c)
    conn.close()
    return context['templates'].TemplateResponse(request, "page/admin/locations.html", {
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
    context = Depends(depend_context)
):
    time_punch_data = None
    if time_punch_json:
        time_punch_data = json.loads(time_punch_json)
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    session = middleware_auth(c, request, ADMIN_USER_ID)
    if session == None:
        return RedirectResponse('/', 303)
    cfa_location = Location.sqlite_find_by_id(c, location_id)
    employees = Employee.sqlite_find_all_by_cfa_location_id(c, cfa_location.id)
    conn.close()
    return context['templates'].TemplateResponse(request, 'page/admin/location.html', context={
        'cfa_location': cfa_location, 
        'employees': employees,
        'session_key': session.key,
        'time_punch_data': time_punch_data,
    })

@app.post('/form/upload/employee_bio')
async def post_form_employee_bio(
    file: Annotated[UploadFile, File()],
    cfa_location_id: str | None = Form(None)
):
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
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

@app.post('/form/cfa_location/create')
async def post_form_cfa_location_create(
    request: Request,
    name: str | None = Form(None), 
    number:str | None = Form(None),
    session_key:str | None = Form(None),
):
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    session = middleware_auth(c, request, ADMIN_USER_ID)
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    potential_location = Location.sqlite_find_by_number(c, number)
    if potential_location != None:
        return RedirectResponse('/admin/cfa_locations?err_create_location=location with provided number already exists', 303)
    Location.sqlite_insert_one(c, name, number)
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
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    session = middleware_auth(c, request, ADMIN_USER_ID)
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

@app.post('/form/employee/update/department')
async def post_form_employee_update_department(
    request: Request,
    department: str | None = Form(None),
    employee_id: str | None = Form(None),
    location_id: str | None = Form(None),
    session_key:str | None = Form(None),
):
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    session = middleware_auth(c, request, ADMIN_USER_ID)
    if session == None or session_key != session.key:
        return RedirectResponse('/', 303)
    Employee.sqlite_update_department(c, employee_id, department)
    conn.commit()
    conn.close()
    return RedirectResponse(f'/admin/cfa_location/{location_id}', 303)

@app.post('/form/upload/time_punch')
async def post_form_upload_time_punch(
    request: Request,
    file: Annotated[UploadFile, File()],
    cfa_location_id: str | None = Form(None),
    session_key:str | None = Form(None),
):
    try:
        contents = await file.read()
        conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
        session = middleware_auth(c, request, ADMIN_USER_ID)
        if session == None or session_key != session.key:
            return RedirectResponse('/', 303)
        current_employees = Employee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)
        time_punch_pdf = TimePunchReader(contents, current_employees)
        conn.close()
        return RedirectResponse(url=f"/admin/cfa_location/{cfa_location_id}?time_punch_json={time_punch_pdf.to_json()}", status_code=303)
    except Exception as e:
        return {"message": str(e)}    

@app.get('/form/logout')
async def post_form_logout(
    response: Response,
    session_key: Optional[str] = None
):
    conn, c = sqlite_connection(SQLITE_ABSOLUTE_PATH)
    if session_key == None:
        return RedirectResponse('/', status_code=303)
    current_session = Session.sqlite_get_by_user_id(c, ADMIN_USER_ID)
    if current_session == None:
        return RedirectResponse('/', status_code=303)
    if session_key != current_session.key:
        return RedirectResponse('/', status_code=303)
    Session.sqlite_delete_by_session_key(c, session_key)
    conn.commit()
    conn.close()
    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie('APP_SESSION_ID', httponly=True, secure=True, samesite='lax')
    return response

