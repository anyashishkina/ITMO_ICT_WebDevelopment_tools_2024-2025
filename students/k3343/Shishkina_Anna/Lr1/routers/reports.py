from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from connection import get_session
from utils.auth_utils import get_current_user
from models import *
from typing import List
from sqlalchemy.orm import joinedload 

router = APIRouter()

@router.get("/")
def get_report(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    # считаем все доходы и расходы
    total_income = sum(t.amount for t in transactions if t.type == TransactionType.income)
    total_expense = sum(t.amount for t in transactions if t.type == TransactionType.expense)
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }

@router.get("/detailed_report")
def get_detailed_report(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    # загружаем категорию и аккаунт для каждой транзакции
    for t in transactions:
        if t.category_id:
            t.category = session.get(Category, t.category_id)
        if t.account_id:
            t.account = session.get(Account, t.account_id)
    
    report = {
        "total_income": sum(t.amount for t in transactions if t.type == TransactionType.income),
        "total_expense": sum(t.amount for t in transactions if t.type == TransactionType.expense),
        "balance": sum(t.amount for t in transactions if t.type == TransactionType.income) - 
                 sum(t.amount for t in transactions if t.type == TransactionType.expense),
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "date": t.date,
                "description": t.description,
                "type": t.type,
                "category_name": t.category.name if hasattr(t, 'category') and t.category else None, # записываем название категории
                "account_name": t.account.name if hasattr(t, 'account') and t.account else None, # записываю название счёта
            }
            for t in transactions
        ]
    }
    return report