from fastapi import HTTPException, Security, Depends
from datetime import timedelta
import jwt
from sqlmodel import Session, select
from models import User
from datetime import datetime
from connection import get_session
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

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
    except JWTError:
        raise HTTPException(status_code=401, detail="Неудалось проверить токен")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    payload = get_current_user_token(token)
    user_email: str = payload.get("sub")
    if user_email is None:
        raise HTTPException(status_code=401, detail="Неизвестный пользователь")
    db_user = session.exec(select(User).filter(User.email == user_email)).first()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return db_user
