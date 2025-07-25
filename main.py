import os
from io import BytesIO
import json
from typing import Annotated, Optional

from fastapi import FastAPI, Request, UploadFile, File, Form, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pandas import read_excel
from dotenv import load_dotenv
load_dotenv() # must call BEFORE loading in modules from ./src

from src.db import *
from src.parse import *
from src.log import *
from src.middleware import *
from src.routes import *

init_tables()

app = FastAPI(dependencies=[Depends(depend_context)])
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_api_route("/", get_index, response_class=HTMLResponse, methods=["GET"])
app.add_api_route("/admin", get_admin, response_class=HTMLResponse, methods=["GET"])
app.add_api_route("/admin/cfa_locations", get_app_locations, response_class=HTMLResponse, methods=["GET"])
app.add_api_route("/admin/cfa_location/{location_id}", get_app_cfa_location, methods=["GET"])
app.add_api_route("/form/login", post_form_login, methods=["POST"])
app.add_api_route("/form/upload/employee_bio", post_form_employee_bio, methods=["POST"])
app.add_api_route("/form/cfa_location/create", post_form_cfa_location_create, methods=["POST"])
app.add_api_route("/form/cfa_location/delete/{id}", post_form_cfa_location_delete, methods=["POST"])
app.add_api_route("/form/employee/update/department", post_form_employee_update_department, methods=["POST"])
app.add_api_route("/form/upload/time_punch", post_form_upload_time_punch, methods=["POST"])
