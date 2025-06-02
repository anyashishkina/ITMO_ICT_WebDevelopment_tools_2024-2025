from fastapi import HTTPException, Request, Depends
from datetime import datetime, timedelta
import jwt
from sqlmodel import Session, select
from typing import Optional
from models import *
from connection import get_session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"

class CustomBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        return await super().__call__(request)

bearer_scheme = CustomBearer()

# генерация jwt токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Получения пользователя из токена
def get_current_user_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный токен")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    payload = get_current_user_token(token)
    user_email: str = payload.get("sub")

    if user_email is None:
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = session.exec(select(User).where(User.email == user_email)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user