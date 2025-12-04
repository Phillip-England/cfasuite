from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from ..config import AppConfig
from ..bots import process_daily_birthdays


def post_tbot_birthday(app: FastAPI, config: AppConfig):
    @app.post("/tbot/birthday")
    async def post_tbot_birthday_endpoint(key: str):
        if key != config.tbot_key:
             return JSONResponse(status_code=401, content={"message": "Unauthorized"})
        
        try:
            # Execute the existing bot logic
            process_daily_birthdays()
            return JSONResponse(status_code=200, content={"message": "Birthday bot executed successfully"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": f"Error running bot: {str(e)}"})