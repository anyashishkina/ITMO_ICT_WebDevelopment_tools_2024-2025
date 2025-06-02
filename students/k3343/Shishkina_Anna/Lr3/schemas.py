from pydantic import BaseModel
from typing import List, Optional
from models import *

class UserWithCategories(SQLModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    categories: List[CategoryRead] = []

    class Config:
        orm_mode = True
