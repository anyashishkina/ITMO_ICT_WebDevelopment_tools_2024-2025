import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

class ParseRequest(BaseModel):
    url: str

@app.post("/parse")
async def parse(request: ParseRequest):
    url = request.url
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                html = await resp.text()

        # Тут вызвать асинхронный парсер, если нужно
        return {"message": "Parsing completed", "content_length": len(html)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
