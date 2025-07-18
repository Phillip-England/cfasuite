import os

from io import BytesIO

from typing import Annotated, Optional

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pandas import read_excel

from dotenv import load_dotenv

from decimal import Decimal, ROUND_HALF_UP

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
    return t.TemplateResponse(request, "page/admin/home.html", {})

@app.get("/admin/cfa_locations", response_class=HTMLResponse)
async def get_app_locations(
    request: Request,
    err_create_location: Optional[str] = ''
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    cfa_locations = DataCfaLocation.sqlite_find_all(c)
    conn.close()
    return t.TemplateResponse(request, "page/admin/cfa_locations.html", {
            "id": id, 
            "cfa_locations": cfa_locations,
            'err_create_location': err_create_location,
        }
    )

@app.get('/admin/cfa_location/{location_id}')
async def get_app_cfa_location(request: Request, location_id: int):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    cfa_location = DataCfaLocation.sqlite_find_by_id(c, location_id)
    employees = DataEmployee.sqlite_find_all_by_cfa_location_id(c, cfa_location.id)
    conn.close()
    return t.TemplateResponse(request, 'page/admin/cfa_location.html', context={''
        'cfa_location': cfa_location, 
        'employees': employees
    })

@app.post('/form/login')
async def post_login(
    username: str | None = Form(None),
    password: str | None = Form(None),
):
    if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
        return RedirectResponse(url='/admin', status_code=303)
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
    name: str | None = Form(None), 
    number:str | None = Form(None)
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    potential_location = DataCfaLocation.sqlite_find_by_number(c, number)
    if potential_location != None:
        return RedirectResponse('/admin/cfa_locations?err_create_location=location with provided number already exists', 303)
    DataCfaLocation.sqlite_insert_one(c, name, number)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin/cfa_locations", status_code=303)

@app.post('/form/cfa_location/delete/{id}')
async def post_form_cfa_location_delete(
    id: int,
    cfa_location_number: int | None = Form(None)
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
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
    department: str | None = Form(None),
    employee_id: str | None = Form(None),
    location_id: str | None = Form(None),
):
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    DataEmployee.sqlite_update_department(c, employee_id, department)
    conn.commit()
    conn.close()
    return RedirectResponse(f'/admin/cfa_location/{location_id}', 303)
    
@app.post("/form/upload/time_punch")
async def post_form_employees_create(
    file: Annotated[UploadFile, File()],
    cfa_location_id: str | None = Form(None)
):
    contents = await file.read()
    time_punch_pdf = TimePunchReader(BytesIO(contents))
    conn = sqlite_connection(sqlite_path)
    c = conn.cursor()
    current_employees = DataEmployee.sqlite_find_all_by_cfa_location_id(c, cfa_location_id)
    init_cost = 0
    boh_cost = 0
    cst_cost = 0
    rlt_cost = 0
    foh_cost = 0
    for time_punch_employee in time_punch_pdf.time_punch_employees:
        for current_employee in current_employees:
            if time_punch_employee.name == current_employee.time_punch_name:
                if current_employee.department == 'INIT':
                    init_cost += time_punch_employee.total_wages
                if current_employee.department == 'BOH':
                    boh_cost += time_punch_employee.total_wages
                if current_employee.department == 'FOH':
                    foh_cost += time_punch_employee.total_wages
                if current_employee.department == 'CST':
                    cst_cost += time_punch_employee.total_wages
                if current_employee.department == 'RLT':
                    rlt_cost += time_punch_employee.total_wages
                break
    foh_percentage = ((foh_cost*100)/time_punch_pdf.total_wages).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rlt_percentage = ((rlt_cost*100)/time_punch_pdf.total_wages).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    cst_percentage = ((cst_cost*100)/time_punch_pdf.total_wages).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    boh_percentage = ((boh_cost*100)/time_punch_pdf.total_wages).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    breakdown = f'''
        INIT COST: {init_cost}
        BOH_COST: {boh_cost}
        BOH_%: {boh_percentage}%
        FOH_COST: {foh_cost}
        FOH_%: {foh_percentage}%
        CST_COST: {cst_cost}
        CST_%: {cst_percentage}%
        RLT_COST: {rlt_cost}
        RLT_%: {rlt_percentage}%
        TOTAL_COST: {time_punch_pdf.total_wages}
    '''
    print(breakdown)
    conn.close()
    return RedirectResponse(url=f"/admin/cfa_location/{cfa_location_id}", status_code=303)