from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DB_ADMIN')
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

session=Depends(get_session)

def save_category(name: str):
    with Session(engine) as session:
        # Проверка, существует ли уже категория с таким названием
        statement = select(Category).where(Category.name == name)
        result = session.exec(statement).first()
        if not result:
            category = Category(name=name)
            session.add(category)
            session.commit()
            print(f"Сохранено: {name}")
        else:
            print(f"Уже существует: {name}")