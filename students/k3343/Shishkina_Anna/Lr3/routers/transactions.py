from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from connection import get_session
from utils.auth_utils import get_current_user
from models import *
from typing import List

router = APIRouter()

@router.post("/", response_model=Transaction)
def create_transaction(transaction: Transaction, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    transaction.user_id = current_user.id

    account = session.get(Account, transaction.account_id)
    if account is None or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Счет не найден или нет доступа")

    # Обновляем баланс счёта в зависимости от типа транзакции
    if transaction.type == TransactionType.income:
        account.balance += transaction.amount
    elif transaction.type == TransactionType.expense:
        if account.balance < transaction.amount:
            raise HTTPException(status_code=400, detail="Недостаточно средств на счете")
        account.balance -= transaction.amount

    session.add(transaction)
    session.add(account)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get("/", response_model=List[Transaction])
def list_transactions(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Transaction).where(Transaction.user_id == current_user.id)).all()


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, transaction: Transaction, 
                     session: Session = Depends(get_session), 
                     current_user: User = Depends(get_current_user)):
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    if db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет доступа")

    # получаем счет, к которому была привязана транзакция и к которому будет привязана транзакция
    old_account = session.get(Account, db_transaction.account_id)
    new_account = session.get(Account, transaction.account_id)
    
    if not old_account or old_account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Старый счёт не найден")
    if not new_account or new_account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Новый счёт не найден")

    # Проверяем достаточно ли средств до изменениями
    if transaction.type == TransactionType.expense:
        if new_account.balance + (db_transaction.amount if db_transaction.type == TransactionType.income else -db_transaction.amount) < transaction.amount:
            raise HTTPException(status_code=400, detail="Недостаточно средств на новом счете")

    # Отменяем старую транзакцию
    if db_transaction.type == TransactionType.income:
        old_account.balance -= db_transaction.amount # Уменьшаем баланс (возвращаем расход)
    else:
        old_account.balance += db_transaction.amount # Увеличиваем баланс (возвращаем доход)

    # Применяем новую транзакцию
    if transaction.type == TransactionType.income:
        new_account.balance += transaction.amount
    else:
        new_account.balance -= transaction.amount

    # Обновляем саму транзакцию
    db_transaction.amount = transaction.amount
    db_transaction.date = transaction.date
    db_transaction.description = transaction.description
    db_transaction.type = transaction.type
    db_transaction.category_id = transaction.category_id
    db_transaction.account_id = transaction.account_id

    session.add(db_transaction)
    session.add(old_account)
    if old_account.id != new_account.id:
        session.add(new_account)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@router.delete("/{transaction_id}", response_model=Transaction)
def delete_transaction(transaction_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    if db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет доступа")

    account = session.get(Account, db_transaction.account_id)
    if account is None or account.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Счёт не найден")

    # Возврат средств 
    if db_transaction.type == TransactionType.income:
        account.balance -= db_transaction.amount
    elif db_transaction.type == TransactionType.expense:
        account.balance += db_transaction.amount

    session.delete(db_transaction)
    session.add(account)
    session.commit()
    return db_transaction