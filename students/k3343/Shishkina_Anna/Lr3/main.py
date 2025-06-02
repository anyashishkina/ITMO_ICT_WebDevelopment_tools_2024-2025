from fastapi import FastAPI, HTTPException
from connection import init_db
from pydantic import BaseModel
from routers import categories, accounts, transactions, budgets, reports
import auth
import aiohttp
import asyncio
import httpx
from celery_app import parse_url_task


app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router, tags=["Auth"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])


class ParseRequest(BaseModel):
    url: str

PARSER_URL = "http://parser_service:8001/parse"

@app.post("/parse")
async def call_parser(request: ParseRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(PARSER_URL, json={"url": request.url})
            response.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Ошибка соединения с парсером: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=f"Ошибка парсера: {e.response.text}")

    return response.json()

@app.post("/parse_async")
async def parse_async(request: ParseRequest):
    task = parse_url_task.delay(request.url)  # ставим задачу в очередь
    return {"task_id": task.id, "status": "Parsing started"}

@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=parse_url_task._app)
    if result.state == "PENDING":
        return {"status": "Pending"}
    elif result.state != "FAILURE":
        return {"status": result.state, "result": result.result}
    else:
        return {"status": "Failure", "error": str(result.result)}