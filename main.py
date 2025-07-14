import io
from io import BytesIO

from typing import Annotated

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pdfminer.high_level import extract_text

from pandas import read_excel

from src.sqlite_db import *
from src.employee import *

sqlite_path = './main.db'

sqlite_table_cfa_locations(sqlite_path)
sqlite_table_employees(sqlite_path)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
t = Jinja2Templates(directory="templates")

@app.get("/app", response_class=HTMLResponse)
async def read_item(r: Request):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    sql, params = Employee.sql_all()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    employees = Employee.many_from_db_rows(rows)
    conn.close()
    return t.TemplateResponse(
        request=r, name="page_app_home.html", context={"id": id, "employees": employees}
    )

@app.get("/app/cfa_locations", response_class=HTMLResponse)
async def get_app_locations(r: Request):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    sql, params = CfaLocation.sql_all()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cfa_locations = CfaLocation.many_from_db_rows(rows)
    conn.close()
    return t.TemplateResponse(
        request=r, name="page_app_locations.html", context={"id": id, "cfa_locations": cfa_locations}
    )

@app.get("/app/employees", response_class=HTMLResponse)
async def get_app_employees(r: Request):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    sql, params = Employee.sql_all()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    employees = Employee.many_from_db_rows(rows)
    conn.close()
    return t.TemplateResponse(
        request=r, name="page_app_employees.html", context={"id": id, "employees": employees}
    )

@app.get("/app/time_punch", response_class=HTMLResponse)
async def get_app_time_punch(r: Request):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    sql, params = Employee.sql_all()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    employees = Employee.many_from_db_rows(rows)
    conn.close()
    return t.TemplateResponse(
        request=r, name="page_app_time_punch.html", context={"id": id}
    )

@app.post("/form/tp")
async def post_form_tp(
    file: Annotated[UploadFile, File()],
):
    contents = await file.read()
    text = extract_text(io.BytesIO(contents))
    return RedirectResponse(url="/", status_code=303)


@app.post("/form/employees/create")
async def post_form_employees_create(
    file: Annotated[UploadFile, File()],
):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    contents = await file.read()
    df = read_excel(BytesIO(contents))
    reader = EmployeeBioReader(df)
    for name in reader.names:
        employee = Employee(name)
        sql, params = employee.sql_find()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        if row == None:
            sql_again, params_again = employee.sql_insert()
            cursor.execute(sql_again, params_again)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post('/form/cfa_location/create')
async def post_form_cfa_location_create(
    name: str = Form(str), 
    number:str = Form(str)
):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    cfa_location = CfaLocation(name, number)
    sql, params = cfa_location.sql_insert()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/app/cfa_locations", status_code=303)


