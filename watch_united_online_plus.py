import os
import json
import requests

BASE = "https://jefunited.co.jp"

API = BASE + "/my/uoplus/list-api"

SEEN_FILE = "seen_united_online_plus.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": BASE + "/my/uoplus/"
}


# -------------------------
# seen管理
# -------------------------

def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen)), f, ensure_ascii=False, indent=2)


# -------------------------
# API取得
# -------------------------

def fetch_page(page: int):
    params = {"page": page}

    r = requests.get(API, headers=HEADERS, params=params, timeout=10)
    r.raise_for_status()

    return r.json()


# -------------------------
# 正規化（ここが重要）
# -------------------------

def normalize(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return (
            data.get("articles")
            or data.get("data")
            or data.get("result")
            or []
        )

    return []


# -------------------------
# 記事抽出
# -------------------------

def extract_articles(data):
    articles = []

    for a in normalize(data):
        if not isinstance(a, dict):
            continue

        url = a.get("url") or a.get("link")
        title = a.get("title") or a.get("name")

        if not url:
            continue

        # 相対URL対応
        if not url.startswith("http"):
            url = BASE + url

        # ゴミURL除外（最低限）
        if "/my/uoplus/" not in url:
            continue

        articles.append({
            "url": url.split("?")[0],
            "title": title or "UNTITLED"
        })

    return articles


# -------------------------
# 全ページ取得
# -------------------------

def fetch_all():
    results = []
    page = 1

    while True:
        data = fetch_page(page)
        articles = extract_articles(data)

        if not articles:
            break

        results.extend(articles)

        page += 1

        if page > 50:  # 安全弁
            break

    # dedupe
    seen = set()
    unique = []

    for a in results:
        if a["url"] in seen:
            continue
        seen.add(a["url"])
        unique.append(a)

    return unique


# -------------------------
# メイン
# -------------------------

def main():
    print("=== START UNITED ONLINE PLUS ===")

    seen = load_seen()
    print("[SEEN]", len(seen))

    articles = fetch_all()
    print("[ARTICLES]", len(articles))

    new_articles = [a for a in articles if a["url"] not in seen]
    print("[NEW]", len(new_articles))

    # 初回は登録のみ
    if not seen and new_articles:
        for a in new_articles:
            seen.add(a["url"])
        save_seen(seen)
        print("[INIT] seed complete")
        return

    # 新着処理
    for a in reversed(new_articles):
        print("[NEW ARTICLE]", a["title"])
        seen.add(a["url"])

        send_discord(a)

    save_seen(seen)

    print("=== DONE UNITED ONLINE PLUS ===")


# -------------------------
# Discord
# -------------------------

def send_discord(article):
    webhook = os.environ.get("UNITEDONLINEPLUS_WEBHOOK")

    if not webhook:
        raise Exception("UNITEDONLINEPLUS_WEBHOOK missing")

    requests.post(
        webhook,
        json={
            "content": "【UNITED ONLINE PLUS更新】\n"
                       f"{article['title']}\n"
                       f"{article['url']}"
        },
        timeout=10
    ).raise_for_status()


# -------------------------
# entry
# -------------------------

if __name__ == "__main__":
    main()
