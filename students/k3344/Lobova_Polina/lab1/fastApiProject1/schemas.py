from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


class CategoryCreate(BaseModel):
    name: str

class CategoryRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    amount: float
    is_income: bool
    description: Optional[str]
    category_ids: List[int] = []

class TransactionRead(BaseModel):
    id: int
    amount: float
    is_income: bool
    timestamp: datetime
    description: Optional[str]
    categories: List[CategoryRead] = []

    class Config:
        from_attributes = True


class BudgetCreate(BaseModel):
    month: str
    limit: float
    category_id: int

class BudgetRead(BaseModel):
    id: int
    month: str
    limit: float
    category: CategoryRead

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    title: str
    target_amount: float
    deadline: Optional[datetime]

class GoalRead(BaseModel):
    id: int
    title: str
    target_amount: float
    current_amount: float
    deadline: Optional[datetime]

    class Config:
        from_attributes = True