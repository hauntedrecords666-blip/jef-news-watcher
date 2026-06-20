import json
import os
import requests
from bs4 import BeautifulSoup

NEWS_URL = "https://jefunited.co.jp/news/list"
SEEN_FILE = "seen.json"

html = requests.get(
    NEWS_URL,
    headers={"User-Agent": "Mozilla/5.0"}
).text

soup = BeautifulSoup(html, "html.parser")

articles = []

for a in soup.find_all("a", href=True):
    href = a["href"]

    if "/news/detail/" in href:
        if href.startswith("/"):
            href = "https://jefunited.co.jp" + href

        title = a.get_text(" ", strip=True)

        if title:
            articles.append({
                "url": href,
                "title": title
            })

# URL重複除去
unique = {}
for a in articles:
    unique[a["url"]] = a

articles = list(unique.values())[:50]


try:
    with open(SEEN_FILE, encoding="utf-8") as f:
        seen = set(json.load(f))
except:
    seen = set()


new_articles = [
    a for a in articles
    if a["url"] not in seen
]


if new_articles:
    message = "\n\n".join(
        [
            f"【ジェフNEWS更新】\n{a['title']}\n{a['url']}"
            for a in reversed(new_articles)
        ]
    )

    requests.post(
        os.environ["DISCORD_WEBHOOK"],
        json={"content": message}
    )

    seen.update(
        a["url"] for a in new_articles
    )


with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(
        list(seen),
        f,
        ensure_ascii=False
    )
