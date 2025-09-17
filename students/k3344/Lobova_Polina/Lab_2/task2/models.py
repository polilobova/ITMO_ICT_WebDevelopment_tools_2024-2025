from typing import Optional, List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime


class ArticleHub(SQLModel, table=True):
    article_id: int = Field(default=None, foreign_key="article.id", primary_key=True)
    hub_id:     int = Field(default=None, foreign_key="hub.id",    primary_key=True)


class Article(SQLModel, table=True):
    id:           Optional[int]   = Field(default=None, primary_key=True)
    title:        str             = Field(index=True)
    url:          str             = Field(index=True)
    published_at: datetime        = Field(sa_column=Column(DateTime, nullable=False))
    flow:         str             = Field(index=True, description="develop/admin/popsci")
    author:       str             = Field(index=True, description="Автор статьи")
    view_count:   int             = Field(default=0, description="Просмотры при парсинге")

    hubs: List["Hub"] = Relationship(back_populates="articles", link_model=ArticleHub)


class Hub(SQLModel, table=True):
    id:   Optional[int] = Field(default=None, primary_key=True)
    name: str           = Field(index=True, unique=True)

    articles: List[Article] = Relationship(back_populates="hubs", link_model=ArticleHub)