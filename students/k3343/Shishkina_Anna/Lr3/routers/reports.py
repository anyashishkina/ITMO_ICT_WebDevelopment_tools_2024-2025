from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from connection import get_session
from utils.auth_utils import get_current_user
from models import *
from typing import List
from schemas import *

router = APIRouter()

@router.get("/")
def get_report(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Получаем только транзакции текущего пользователя
    transactions = session.exec(
        select(Transaction).where(Transaction.user_id == current_user.id)
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.type == TransactionType.income)
    total_expense = sum(t.amount for t in transactions if t.type == TransactionType.expense)
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }

@router.get("/detailed_report")
def get_detailed_report(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Получаем только транзакции текущего пользователя
    transactions = session.exec(
        select(Transaction).where(Transaction.user_id == current_user.id)
    ).all()
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
                "category_name": t.category.name if t.category else None, # записываем название категории
                "account_name": t.account.name if t.account else None, # записываю название счёта
                "account_id": t.account_id
            }
            for t in transactions
        ]
    }
    return report

@router.get("/users-with-categories", response_model=List[UserWithCategories])
def get_users_with_categories(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users