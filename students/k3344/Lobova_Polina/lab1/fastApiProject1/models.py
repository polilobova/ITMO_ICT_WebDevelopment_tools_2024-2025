from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class TransactionCategoryLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(default=None, foreign_key="transaction.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str

    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    transactions: List["Transaction"] = Relationship(
        back_populates="categories",
        link_model=TransactionCategoryLink,
    )
    budgets: List["Budget"] = Relationship(back_populates="category")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    is_income: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="transactions")

    categories: List[Category] = Relationship(
        back_populates="transactions",
        link_model=TransactionCategoryLink,
    )

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    month: str
    limit: float

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="budgets")

    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="budgets")

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[datetime] = None

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="goals")