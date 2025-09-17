import threading
import time
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, select, Session, create_engine
from models import Article, Hub, ArticleHub

"""
All done in 1.92s
"""

SYNC_DATABASE_URL = "sqlite:///./lab1.db"


engine = create_engine(
    SYNC_DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
)

# Список URL Habr по направлениям топиков
HABR_FLOWS = [
    "https://habr.com/ru/flows/develop/articles/",
    "https://habr.com/ru/flows/admin/articles/",
    "https://habr.com/ru/flows/popsci/articles/",
]

def parse_and_save(flow_url: str):
    print(f"→ [{threading.current_thread().name}] Parsing {flow_url}")
    try:
        resp = requests.get(
            flow_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"  ✖ [{threading.current_thread().name}] Fetch error: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")
    snippets = soup.select("article.tm-articles-list__item")
    print(f"  • [{threading.current_thread().name}] Snippets found: {len(snippets)}")

    with Session(engine) as session:
        for snip in snippets:

            a_title = snip.select_one("h2.tm-title a.tm-title__link")
            if not a_title:
                continue
            title = a_title.get_text(strip=True)
            link  = urljoin(flow_url, a_title["href"])

            time_tag = snip.select_one("time[datetime]")
            published = datetime.fromisoformat(time_tag["datetime"]) if time_tag else datetime.utcnow()

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
                flow=flow_url.rstrip("/").split("/")[-2],
                author=author,
                view_count=view_count
            )
            session.add(article)
            session.commit()

            for hub_name in hubs:
                result = session.exec(select(Hub).where(Hub.name == hub_name))
                hub = result.one_or_none()
                if not hub:
                    hub = Hub(name=hub_name)
                    session.add(hub)
                    session.commit()
                session.add(ArticleHub(article_id=article.id, hub_id=hub.id))
            session.commit()

            print(f"  • [{threading.current_thread().name}] '{title[:30]}…' by {author}, views={view_count}")

    print(f"✔ [{threading.current_thread().name}] Done {flow_url}\n")

def main():
    SQLModel.metadata.create_all(engine)

    start = time.time()
    threads = []
    for url in HABR_FLOWS:
        th = threading.Thread(target=parse_and_save, args=(url,), name=url.split("/")[-3])
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    print(f"All done in {time.time() - start:.2f}s")

if __name__ == '__main__':
    main()