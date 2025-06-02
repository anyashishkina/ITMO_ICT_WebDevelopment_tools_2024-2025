from fastapi import APIRouter, Depends, HTTPException, Form
from sqlmodel import Session, select
from connection import get_session
from models import *
from utils.auth_utils import create_access_token, get_current_user
from utils.security import hash_password, verify_password

router = APIRouter()

@router.post("/register")
def register_user(user: UserCreateWithPassword, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).filter(User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, full_name=user.full_name, hashed_password=hashed_password, is_active=True)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/login")
def login_user(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    db_user = session.exec(select(User).filter(User.email == username)).first()
    if db_user is None or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[UserRead])
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@router.put("/change_password")
def change_password(new_password: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    hashed_password = hash_password(new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return {"msg": "Пароль успешно изменен"}
