from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from connection import get_session
from utils.auth_utils import get_current_user
from models import *
from typing import List

router = APIRouter()

@router.post("/", response_model=Account)
def create_account(account: Account, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    account.user_id = current_user.id
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.get("/", response_model=List[Account])
def list_accounts(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(select(Account).where(Account.user_id == user.id)).all()

@router.put("/{account_id}", response_model=Account)
def update_account(
    account_id: int, 
    account_update: AccountUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Счет не найден")
    if db_account.user_id != current_user.id: #если введен аккаунт другого пользователя
        raise HTTPException(status_code=403, detail="У вас нет доступа")
    
    # Обновление полей
    if account_update.name is not None:
        db_account.name = account_update.name
    if account_update.balance is not None:
        db_account.balance = account_update.balance
    if account_update.account_type is not None:
        db_account.account_type = account_update.account_type
    
    session.commit()
    session.refresh(db_account)
    return db_account

@router.delete("/{account_id}", response_model=Account)
def delete_account(account_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_account = session.get(Account, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Счет не найден")
    if db_account.user_id != current_user.id: #если введен аккаунт другого пользователя
        raise HTTPException(status_code=403, detail="У вас нет доступа")
    session.delete(db_account)
    session.commit()
    return db_account
