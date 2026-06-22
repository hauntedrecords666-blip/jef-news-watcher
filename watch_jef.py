import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


LIST_URL = "https://jefunited.co.jp/news/list"
SEEN_FILE = "seen.json"


def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


def fetch_list():
    r = requests.get(
        LIST_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    )

    if r.status_code != 200:
        print("list fetch failed:", r.status_code)
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    articles = []

    # aタグから /news/detail/ を拾う
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/news/detail/" not in href:
            continue

        url = urljoin(LIST_URL, href)

        title = a.get_text(" ", strip=True)

        if not title:
            continue

        articles.append({
            "url": url,
            "title": title
        })

    # 重複排除
    unique = {}
    for a in articles:
        unique[a["url"]] = a

    return list(unique.values())


def send_discord(article):
    requests.post(
        os.environ["DISCORD_WEBHOOK"],
        json={
            "content": (
                "【ジェフNEWS更新】\n"
                f"{article['title']}\n"
                f"{article['url']}"
            )
        },
        timeout=10
    )


def main():
    seen = load_seen()

    articles = fetch_list()

    if not articles:
        print("no articles fetched")
        return

    # 新規判定
    new_articles = [
        a for a in articles
        if a["url"] not in seen
    ]

    # 日付順っぽく安定化（URL or DOM順）
    new_articles = list(reversed(new_articles))

    if not seen and new_articles:
        # 初回は最新だけ登録（暴発防止）
        latest = new_articles[0]
        seen.add(latest["url"])
        save_seen(seen)
        print("initial run, skipped sending")
        return

    for article in new_articles:
        send_discord(article)
        seen.add(article["url"])

    save_seen(seen)
    print(f"sent {len(new_articles)} articles")


if __name__ == "__main__":
    main()
