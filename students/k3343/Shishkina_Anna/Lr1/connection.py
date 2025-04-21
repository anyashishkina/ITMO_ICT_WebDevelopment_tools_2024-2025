from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends

db_url = 'postgresql://annashishkina:annashishkina@localhost/lab1_db'
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

session=Depends(get_session)
