from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

import os
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "lab2.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# асинхронный движок
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

def get_async_session() -> AsyncSession:
    return AsyncSessionLocal()

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)