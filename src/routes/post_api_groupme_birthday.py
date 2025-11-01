from fastapi import FastAPI
from fastapi.responses import JSONResponse

from ..config import AppConfig

def post_api_groupme_birthday(app: FastAPI, config: AppConfig):
    app.post('/api/groupme/birthday')
    async def post_api_groupme_bithday():
        return JSONResponse(status_code=200, content={"message": "hit"})
    