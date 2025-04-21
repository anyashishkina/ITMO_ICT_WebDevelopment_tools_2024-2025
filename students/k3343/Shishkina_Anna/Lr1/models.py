from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date
from enum import Enum
from pydantic import EmailStr
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional

# Пользователь
class UserBase(SQLModel):
    email: EmailStr
    full_name: Optional[str] = None


class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = True

    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")
    accounts: List["Account"] = Relationship(back_populates="user")

# Категории трат
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    user_id: int = Field(foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="categories")
    
    budgets: List["Budget"] = Relationship(back_populates="category")
    transactions: List["Transaction"] = Relationship(back_populates="category")

# Счета
class AccountType(str, Enum):
    checking = "checking"  # Расчетный счет
    savings = "savings"    # Сберегательный счет
    credit = "credit"      # Кредитный счет


class AccountBase(SQLModel):
    user_id: int
    name: str  
    balance: float = 0.0 
    account_type: AccountType


class Account(AccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="accounts")
    transactions: List["Transaction"] = Relationship(back_populates="account")

class AccountUpdate(SQLModel):
    name: Optional[str] = None
    balance: Optional[float] = None
    account_type: Optional[AccountType] = None

# Транзакции
class TransactionType(str, Enum):
    income = "income" # доход
    expense = "expense" # расход

class TransactionBase(SQLModel):
    amount: float
    date: date
    description: Optional[str] = None
    type: TransactionType
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    account_id: Optional[int] = Field(default=None, foreign_key="account.id")

class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="transactions")

    category: Optional[Category] = Relationship(back_populates="transactions")
    account: Optional[Account] = Relationship(back_populates="transactions")


User.accounts = Relationship(back_populates="user")
Transaction.account = Relationship(back_populates="transactions")

# Бюджет на категории
class BudgetBase(SQLModel):
    user_id: int
    amount: float
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="budgets")

    category: Optional[Category] = Relationship(back_populates="budgets")

class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool

class UserCreateWithPassword(UserCreate):
    password: str