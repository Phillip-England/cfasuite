from fastapi.templating import Jinja2Templates


def depend_context():
    templates = Jinja2Templates(directory="templates")
    return {"templates": templates}
