import json
import os
import requests
from bs4 import BeautifulSoup

BASE = "https://jefunited.co.jp/news/detail/"
SEEN_FILE = "seen.json"

try:
    with open(SEEN_FILE, encoding="utf-8") as f:
        seen = set(json.load(f))
except:
    seen = set()

# ここは後で自動化できる
# とりあえず現在値付近
numbers = range(5200, 5230)

articles = []

for n in numbers:
    url = BASE + str(n)

    r = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    )

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.text if soup.title else f"NEWS {n}"

        articles.append({
            "url": url,
            "title": title
        })


new_articles = [
    a for a in articles
    if a["url"] not in seen
]


if new_articles:

    for a in reversed(new_articles):

        requests.post(
            os.environ["DISCORD_WEBHOOK"],
            json={
                "content":
                f"【ジェフNEWS更新】\n{a['title']}\n{a['url']}"
            }
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
