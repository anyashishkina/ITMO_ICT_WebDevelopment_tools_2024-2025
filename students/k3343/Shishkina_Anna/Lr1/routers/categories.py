from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from connection import get_session
from utils.auth_utils import get_current_user
from models import *
from typing import List

router = APIRouter()

@router.post("/", response_model=Category)
def create_category(category: Category, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category.user_id = user.id
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.get("/", response_model=List[Category])
def list_categories(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(select(Category).filter(Category.user_id == user.id)).all()

@router.put("/{category_id}", response_model=Category)
def update_category(category_id: int, updated_category: Category, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category = session.get(Category, category_id)
    if not category or category.user_id != user.id:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    if category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет доступа")
    category.name = updated_category.name
    session.commit()
    session.refresh(category)
    return category

@router.delete("/{category_id}", response_model=Category)
def delete_category(category_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category = session.get(Category, category_id)
    if not category or category.user_id != user.id:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    if category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет доступа")
    session.delete(category)
    session.commit()
    return category
