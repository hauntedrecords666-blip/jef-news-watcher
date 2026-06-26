import json
import os
import re
import requests
from bs4 import BeautifulSoup

NEWS_URL = "https://www.frontale.co.jp/info/"
BASE_URL = "https://www.frontale.co.jp"

SEEN_FILE = "seen_frontale.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# -------------------------
# seen管理
# -------------------------
def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            sorted(list(seen)),
            f,
            ensure_ascii=False,
            indent=2
        )


# -------------------------
# 記事取得（安定版）
# -------------------------
def get_articles():
    try:
        r = requests.get(
            NEWS_URL,
            headers=HEADERS,
            timeout=10
        )
    except Exception as e:
        print("request error:", e)
        return []

    if r.status_code != 200:
        print("status error:", r.status_code)
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    articles = []

    # ★重要：info配下だけに限定（事故防止）
    links = soup.select("a[href*='/info/']")

    for a in links:
        href = a.get("href")
        if not href:
            continue

        # 絶対URL化
        if href.startswith("/"):
            url = BASE_URL + href
        else:
            url = href

        # 年月構造チェック（フロンターレ仕様）
        if not re.search(r"/info/\d{4}/\d{2}/.*\.html$", url):
            continue

        title = a.get_text(" ", strip=True)

        if not title:
            continue

        articles.append({
            "url": url,
            "title": title
        })

    # 重複排除（保険）
    seen_urls = set()
    unique_articles = []

    for a in articles:
        if a["url"] in seen_urls:
            continue
        seen_urls.add(a["url"])
        unique_articles.append(a)

    return unique_articles


# -------------------------
# Discord送信
# -------------------------
def send_discord(article):
    webhook = os.environ.get("FRONTALE_WEBHOOK")

    if not webhook:
        print("ERROR: FRONTALE_WEBHOOK is missing")
        return

    try:
        res = requests.post(
            webhook,
            json={
                "content":
                f"【川崎フロンターレNEWS更新】\n"
                f"{article['title']}\n"
                f"{article['url']}"
            },
            timeout=10
        )

        print("discord status:", res.status_code)

        if res.status_code >= 400:
            print("discord error body:", res.text)

    except Exception as e:
        print("discord exception:", e)


# -------------------------
# main
# -------------------------
def main():
    seen = load_seen()

    articles = get_articles()

    print("DEBUG articles:", len(articles))

    new_articles = [
        a for a in articles
        if a["url"] not in seen
    ]

    print("DEBUG new:", len(new_articles))

    for article in reversed(new_articles):

        print("sending:", article["title"])

        send_discord(article)

        seen.add(article["url"])

    save_seen(seen)

    print("done")


if __name__ == "__main__":
    main()
