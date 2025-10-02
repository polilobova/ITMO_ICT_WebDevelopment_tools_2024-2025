from sqlmodel import SQLModel, Field
from typing import Optional

class ParsedTag(SQLModel, table=True):
    """Теги, полученные при парсинге (отдельная таблица от основной системы)"""
    tag_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    source_url: str