from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship


class TaskTag(SQLModel, table=True):
    """Промежуточная таблица для связи many-to-many между Task и Tag с дополнительными полями."""
    task_id: Optional[int] = Field(default=None, foreign_key="task.task_id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.tag_id", primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    importance_level: int = Field(default=1, ge=1, le=3)

    task: Optional["Task"] = Relationship(back_populates="task_tags")
    tag: Optional["Tag"] = Relationship(back_populates="task_tags")


class User(SQLModel, table=True):
    """Пользователь системы."""
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    birthday: Optional[date] = Field(default=None, nullable=True)
    password: str
    email: str

    tasks: List["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """Задача пользователя."""
    task_id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    due_date: Optional[date]
    priority: Optional[int]
    status: Optional[str]

    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    user: Optional[User] = Relationship(back_populates="tasks")

    time_logs: List["TimeLog"] = Relationship(back_populates="task")
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTag)
    task_tags: List[TaskTag] = Relationship(back_populates="task")


class TimeLog(SQLModel, table=True):
    """Лог времени для задачи."""
    timelog_id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.task_id")
    start_time: datetime
    end_time: datetime
    duration: Optional[int]

    task: Optional[Task] = Relationship(back_populates="time_logs")


class Tag(SQLModel, table=True):
    """Тег для задач."""
    tag_id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    tasks: List[Task] = Relationship(back_populates="tags", link_model=TaskTag)
    task_tags: List[TaskTag] = Relationship(back_populates="tag")