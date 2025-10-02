import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session, select
from parser.models import ParsedTag
import os

DATABASE_URL = os.getenv("DB_URL")
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

async def fetch_and_save(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url, timeout=10) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            tag_elements = soup.select("a.tag")

            with Session(engine) as db_session:
                tags_count = 0
                for tag_el in tag_elements:
                    tag_name = tag_el.text.strip()
                    if tag_name:
                        exists = db_session.exec(select(ParsedTag).where(ParsedTag.name == tag_name)).first()
                        if not exists:
                            db_session.add(ParsedTag(name=tag_name, source_url=url))
                            tags_count += 1
                db_session.commit()
                if tags_count > 0:
                    print(f"[Async] Сохранено {tags_count} тегов с {url}")
    except Exception as e:
        print(f"[Async] Ошибка при обработке {url}: {e}")

async def run_parser(urls: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)