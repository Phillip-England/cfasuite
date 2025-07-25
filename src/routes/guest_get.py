from fastapi import Request, Depends

from ..server import *

async def get_index(request: Request, context = Depends(depend_context)):
    return context['templates'].TemplateResponse(request, 'page/guest/home.html', {})

