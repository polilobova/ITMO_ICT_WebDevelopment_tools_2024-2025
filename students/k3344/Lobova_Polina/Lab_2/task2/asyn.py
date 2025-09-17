import aiohttp
import asyncio
import time
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from connection import get_async_session, init_db
from sqlmodel import select
from models import Article, Hub, ArticleHub

HABR_FLOWS = [
    "https://habr.com/ru/flows/develop/articles/",
    "https://habr.com/ru/flows/admin/articles/",
    "https://habr.com/ru/flows/popsci/articles/",
]


async def parse_and_save(flow_url: str, session: aiohttp.ClientSession):
    print(f"→ Parsing {flow_url}")
    try:
        resp = await session.get(flow_url, timeout=10)
        resp.raise_for_status()
        html = await resp.text()
    except Exception as e:
        print(f"  ✖ Fetch error: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")
    snippets = soup.select("article.tm-articles-list__item")
    print(f"  • Snippets found: {len(snippets)}")

    db = get_async_session()
    for snip in snippets:
        a_title = snip.select_one("h2.tm-title a.tm-title__link")
        if not a_title:
            continue
        title = a_title.get_text(strip=True)
        link  = urljoin(flow_url, a_title["href"])

        time_tag = snip.select_one("time[datetime]")
        published = (
            datetime.fromisoformat(time_tag["datetime"])
            if time_tag else
            datetime.utcnow()
        )

        author_el = snip.select_one("a.tm-user-info__username")
        author = author_el.get_text(strip=True) if author_el else "unknown"

        vc_el = snip.select_one("span.tm-icon-counter__value[title]")
        view_count = int(vc_el["title"]) if vc_el and vc_el.has_attr("title") else 0

        hubs = []
        for a_hub in snip.select("a.tm-publication-hub__link"):
            span = a_hub.select_one("span")
            if span:
                hubs.append(span.get_text(strip=True))
        hubs = list(dict.fromkeys(hubs))

        article = Article(
            title=title,
            url=link,
            published_at=published,
            flow=flow_url.rstrip("/").split("/")[-1],
            author=author,
            view_count=view_count
        )
        db.add(article)
        await db.commit()

        for hub_name in hubs:
            result = await db.exec(select(Hub).where(Hub.name == hub_name))
            # hub = result.scalar_one_or_none()
            hub = result.one_or_none()
            if not hub:
                hub = Hub(name=hub_name)
                db.add(hub)
                await db.commit()
            db.add(ArticleHub(article_id=article.id, hub_id=hub.id))
        await db.commit()

        print(f"  • [{article.flow}] «{title[:30]}…» by {author}, views={view_count}")

    await db.close()
    print(f"✔ Done {flow_url}\n")


async def main():
    await init_db()

    start = time.time()
    async with aiohttp.ClientSession(headers={"User-Agent":"Mozilla/5.0"}) as session:
        await asyncio.gather(*(parse_and_save(url, session) for url in HABR_FLOWS))
    print(f"All done in {time.time() - start:.2f}s")


if __name__ == '__main__':
    asyncio.run(main())