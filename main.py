import sys

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src import *

try:
    config = AppConfig.load()
    init_tables(config.sqlite_absolute_path)

    app = FastAPI(dependencies=[Depends(depend_context)])
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500, content={"message": f"Oops! Something went wrong: {exc}"}
        )

    get_index(app, config)
    get_admin(app, config)
    post_api_groupme_birthday(app, config)
    get_admin_locations(app, config)
    get_admin_cfa_location(app, config)
    post_form_upload_employee_bio(app, config)
    post_form_cfa_location_create(app, config)
    post_form_cfa_location_delete(app, config)
    post_form_employee_update_department(app, config)
    post_form_login(app, config)
    post_form_upload_employee_bio(app, config)
    post_form_upload_employee_birthday_report(app, config)
    post_form_upload_time_punch(app, config)
    get_form_logout(app, config)
    post_form_upload_hotschedules_staff_html(app, config)


except Exception as e:
    print(e)
    sys.exit(1)
