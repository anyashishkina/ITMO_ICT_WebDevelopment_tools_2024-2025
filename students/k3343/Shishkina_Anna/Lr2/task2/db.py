from sqlmodel import SQLModel, Session, create_engine, select
from models import Category

DATABASE_URL = "postgresql://annashishkina:annashishkina@localhost/lab1_db"  
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

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
