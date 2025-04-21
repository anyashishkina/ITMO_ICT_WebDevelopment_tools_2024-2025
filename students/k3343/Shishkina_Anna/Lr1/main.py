from fastapi import FastAPI
from connection import init_db
from routers import categories, accounts, transactions, budgets, reports
import auth

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
