import io
from io import BytesIO

from typing import Annotated

from fastapi import FastAPI, Request, UploadFile, File, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pdfminer.high_level import extract_text

from pandas import read_excel

from sqlite_db import *
from employee import *

sqlite_path = './main.db'

sqlite_table_employees(sqlite_path)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
t = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(r: Request):
    conn = sqlite_connection(sqlite_path)
    cursor = conn.cursor()
    sql, params = Employee.sql_all()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    employees = Employee.many_from_db_rows(rows)
    conn.close()
    return t.TemplateResponse(
        request=r, name="page_guest_home.html", context={"id": id, "employees": employees}
    )

@app.post("/form/tp")
async def post_time_punch(
    file: Annotated[UploadFile, File()],
):
    contents = await file.read()
    text = extract_text(io.BytesIO(contents))
    return RedirectResponse(url="/", status_code=303)


@app.post("/form/bio")
async def post_employee_bio(
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
        print(row)
        if row == None:
            sql_again, params_again = employee.sql_insert()
            cursor.execute(sql_again, params_again)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)
