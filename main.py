import os

import io
from io import BytesIO

from typing import Annotated, Optional

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pdfminer.high_level import extract_text

from pandas import read_excel

from dotenv import load_dotenv

from src.db_sqlite import *
from src.data_employee import *

load_dotenv()

sqlite_path = './main.db'

sqlite_table_cfa_locations(sqlite_path)
sqlite_table_employees(sqlite_path)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
t = Jinja2Templates(directory="templates")

@app.get('/err', response_class=HTMLResponse)
async def get_err(r: Request, status: Optional[str] = '200', message: Optional[str] = 'no error present'):
    print(status)
    return t.TemplateResponse(r, 'page_err.html', {'id': id, 'status': status, 'message': message})


@app.get('/', response_class=HTMLResponse)
async def get_index(r: Request):
    return t.TemplateResponse(
        request=r, name='page_guest_home.html', context={"id": id}
    )

@app.get("/admin", response_class=HTMLResponse)
async def read_item(r: Request):
    return t.TemplateResponse(
        request=r, name="page_admin_home.html", context={"id": id}
    )

@app.get("/admin/cfa_locations", response_class=HTMLResponse)
async def get_app_locations(
    r: Request,
    err_create_location: Optional[str] = ''
):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    sql, params = CfaLocation.sql_select_all()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cfa_locations = CfaLocation.many_from_db_rows(rows)
    conn.close()
    return t.TemplateResponse(
        request=r, name="page_admin_cfa_locations.html", context={
            "id": id, 
            "cfa_locations": cfa_locations,
            'err_create_location': err_create_location,
        }
    )

@app.get('/admin/cfa_location/{id}')
async def get_app_cfa_location(r: Request, id: int):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    sql, params = CfaLocation.sql_find_by_id(id)
    cursor.execute(sql, params)
    row = cursor.fetchone()
    cfa_location = CfaLocation.one_from_db_row(row)
    sql_employee, params_employee = Employee.sql_find_all_by_cfa_location_id(cfa_location.id)
    cursor.execute(sql_employee, params_employee)
    rows = cursor.fetchall()
    print(rows)
    employees = Employee.many_from_db_rows(rows)
    conn.close()
    return t.TemplateResponse(request=r, name='page_admin_cfa_location.html', context={'id': id, 'cfa_location': cfa_location, 'employees': employees})

@app.post('/form/login')
async def post_login(
    username: str | None = Form(None),
    password: str | None = Form(None),
):
    if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
        return RedirectResponse(url='/admin', status_code=303)
    return RedirectResponse(url='/', status_code=303)

@app.post("/form/employees/create")
async def post_form_employees_create(
    file: Annotated[UploadFile, File()],
    cfa_location_id: str = Form(str)
):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    contents = await file.read()
    df = read_excel(BytesIO(contents))
    reader = EmployeeBioReader(df)
    for name in reader.names:
        employee = Employee(name, cfa_location_id)
        sql, params = employee.sql_find_by_name()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        if row == None:
            sql_again, params_again = employee.sql_insert_one()
            cursor.execute(sql_again, params_again)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post('/form/cfa_location/create')
async def post_form_cfa_location_create(
    name: str | None = Form(None), 
    number:str | None = Form(None)
):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    existing_sql, existing_params = CfaLocation.sql_find_by_number(number)
    cursor.execute(existing_sql, existing_params)
    potential_row = cursor.fetchone()
    if potential_row != None:
        return RedirectResponse('/admin/cfa_locations?err_create_location=location with provided number already exists', 303)
    cfa_location = CfaLocation(name, number)
    sql, params = cfa_location.sql_insert_one()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/cfa_locations", status_code=303)

@app.post('/form/cfa_location/delete/{id}')
async def post_form_cfa_location_delete(r: Request, id: int, cfa_location_number: int | None = Form(None)):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    get_sql, get_params = CfaLocation.sql_find_by_id(id)
    cursor.execute(get_sql, get_params)
    row = cursor.fetchone()
    if row == None:
        return JSONResponse({'message': 'unauthorized'}, 401)
    cfa_location = CfaLocation.one_from_db_row(row)
    if cfa_location.number != cfa_location_number:
        print(cfa_location.number, cfa_location_number)
        return JSONResponse({'message': 'unauthorized'}, 401)
    delete_sql, delete_params = CfaLocation.sql_delete_by_id(id)
    cursor.execute(delete_sql, delete_params)
    conn.commit()
    conn.close()
    return RedirectResponse('/admin/cfa_locations', 303)


