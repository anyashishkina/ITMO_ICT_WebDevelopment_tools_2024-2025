# from fastapi import APIRouter, Depends, HTTPException
# from sqlmodel import Session, select
# from connection import get_session
# from utils.auth_utils import get_current_user
# from models import *
# from typing import List

# router = APIRouter()

# @router.post("/", response_model=Category)
# def create_category(category: Category, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
#     category.user_id = user.id
#     session.add(category)
#     session.commit()
#     session.refresh(category)
#     return category

# @router.get("/", response_model=List[Category])
# def list_categories(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
#     return session.exec(select(Category).filter(Category.user_id == user.id)).all()

# @router.put("/{category_id}", response_model=Category)
# def update_category(category_id: int, updated_category: Category, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
#     category = session.get(Category, category_id)
#     if not category or category.user_id != user.id:
#         raise HTTPException(status_code=404, detail="Категория не найдена")
#     if category.user_id != user.id:
#         raise HTTPException(status_code=403, detail="У вас нет доступа")
#     category.name = updated_category.name
#     session.commit()
#     session.refresh(category)
#     return category

# @router.delete("/{category_id}", response_model=Category)
# def delete_category(category_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
#     category = session.get(Category, category_id)
#     if not category or category.user_id != user.id:
#         raise HTTPException(status_code=404, detail="Категория не найдена")
#     if category.user_id != user.id:
#         raise HTTPException(status_code=403, detail="У вас нет доступа")
#     session.delete(category)
#     session.commit()
#     return category
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from connection import get_session
from utils.auth_utils import get_current_user
from models import *
from typing import List

router = APIRouter()

# Создание новой категории (без привязки к пользователю)
@router.post("/", response_model=CategoryRead)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    db_category = Category.from_orm(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

# Привязка категории к пользователю
@router.post("/link", response_model=CategoryRead)
def link_category_to_user(link_data: LinkCategoryToUser, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category = session.get(Category, link_data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    link = session.exec(
        select(UserCategoryLink).where(
            UserCategoryLink.user_id == user.id,
            UserCategoryLink.category_id == category.id
        )
    ).first()

    if link:
        raise HTTPException(status_code=400, detail="Категория уже привязана")

    new_link = UserCategoryLink(user_id=user.id, category_id=category.id)
    session.add(new_link)
    session.commit()
    return category

# Удаление связи между категорией и пользователем
@router.delete("/unlink/{category_id}")
def unlink_category(category_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    link = session.exec(
        select(UserCategoryLink).where(
            UserCategoryLink.user_id == user.id,
            UserCategoryLink.category_id == category_id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    session.delete(link)
    session.commit()
    return {"detail": "Категория отвязана"}

# Получение всех категорий пользователя
@router.get("/", response_model=List[CategoryRead])
def list_user_categories(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    statement = (
        select(Category)
        .join(UserCategoryLink, UserCategoryLink.category_id == Category.id)
        .where(UserCategoryLink.user_id == user.id)
    )
    return session.exec(statement).all()
