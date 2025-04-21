from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from connection import get_session
from utils.auth_utils import get_current_user
from models import *
from typing import List

router = APIRouter()

@router.post("/", response_model=Budget)
def create_budget(budget: Budget, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    budget.user_id = current_user.id
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget

@router.get("/", response_model=List[Budget])
def list_budgets(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Budget).where(Budget.user_id == current_user.id)).all()

@router.get("/budget_status")
def check_budget_status(session: Session = Depends(get_session)):
    budgets = session.exec(select(Budget)).all()
    transactions = session.exec(select(Transaction)).all()

    category_expenses = {}
    for t in transactions:
        if t.type == TransactionType.expense:
            category_expenses[t.category_id] = category_expenses.get(t.category_id, 0) + t.amount

    alerts = []
    for b in budgets:
        spent = category_expenses.get(b.category_id, 0)
        if spent > b.amount:
            alerts.append(f"Превышение бюджета по категории ID {b.category_id}: потрачено {spent}, лимит {b.amount}")

    return {"alerts": alerts}