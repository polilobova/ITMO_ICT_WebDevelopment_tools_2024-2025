from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel
from pydantic import EmailStr, BaseModel



class UserCreate(SQLModel):
    username: str
    password: str
    email: str


class UserRead(SQLModel):
    user_id: int
    username: str
    email: str


class TaskBase(SQLModel):
    title: str
    description: Optional[str]
    due_date: Optional[date]
    priority: Optional[int]
    status: Optional[str]


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    task_id: int
    user_id: int


class TaskUpdate(SQLModel):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[date]
    priority: Optional[int]
    status: Optional[str]


class TagBase(SQLModel):
    name: str


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    tag_id: int


class TaskTagRead(SQLModel):
    task_id: int
    tag_id: int
    created_at: datetime
    importance_level: int
    tag: TagRead


class TagReadWithImportanceLevel(SQLModel):
    tag_id: int
    name: str
    importance_level: int
    created_at: datetime


class TaskReadWithTags(TaskRead):
    tags: List[TagReadWithImportanceLevel] = []


class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str

class UserRead(SQLModel):
    user_id: int
    username: str
    email: EmailStr

class UserLogin(SQLModel):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class ChangePassword(SQLModel):
    old_password: str
    new_password: str


class ParseRequest(BaseModel):
    urls: list[str]