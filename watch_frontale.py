import json
import os
import requests
from bs4 import BeautifulSoup


NEWS_URL = "https://www.frontale.co.jp/info/"
SEEN_FILE = "seen_frontale.json"


def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            list(seen),
            f,
            ensure_ascii=False,
            indent=2
        )


seen = load_seen()


r = requests.get(
    NEWS_URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=10
)


soup = BeautifulSoup(
    r.text,
    "html.parser"
)


articles = []


for a in soup.find_all("a", href=True):

    url = a["href"]

    if "/info/" in url and url.endswith(".html"):

        if url.startswith("/"):
            url = "https://www.frontale.co.jp" + url


        title = a.get_text(
            " ",
            strip=True
        )


        if title:

            articles.append({
                "url": url,
                "title": title
            })



new_articles = [
    a for a in articles
    if a["url"] not in seen
]


# 初回は登録だけ
if not seen:

    for a in new_articles:
        seen.add(a["url"])

else:

    for a in reversed(new_articles):

        requests.post(
            os.environ["DISCORD_WEBHOOK"],
            json={
                "content":
                f"【川崎フロンターレNEWS更新】\n"
                f"{a['title']}\n"
                f"{a['url']}"
            },
            timeout=10
        )

        seen.add(a["url"])


save_seen(seen)
