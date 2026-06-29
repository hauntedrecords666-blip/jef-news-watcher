import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://jefunited.co.jp"
TOP_URL = "https://jefunited.co.jp/my/uoplus/"
SEEN_FILE = "seen_united_online_plus.json"

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
    except FileNotFoundError:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen)), f, ensure_ascii=False, indent=2)


# -------------------------
# HTTP
# -------------------------

def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


# -------------------------
# 記事抽出（核心）
# -------------------------

def extract_articles_from_soup(soup, base_url):
    articles = []
    seen_urls = set()

    # aタグ総走査（最も壊れにくい）
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if not href:
            continue

        url = urljoin(base_url, href).split("?")[0]

        # uoplus記事だけ
        if "/my/uoplus/detail/" not in url:
            continue

        # ゴミ除外（必要なら追加）
        if "/detail/c/mail/" in url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        # タイトル取得（フォールバック付き）
        title = a.get_text(" ", strip=True)

        if not title:
            parent = a.find_parent()
            if parent:
                title = parent.get_text(" ", strip=True)

        if not title:
            title = "UNITED ONLINE PLUS"

        articles.append({
            "url": url,
            "title": title
        })

    return articles


# -------------------------
# カテゴリ取得
# -------------------------

def get_categories():
    print("[CATEGORY] fetching")

    soup = get_soup(TOP_URL)

    categories = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/my/uoplus/list?c=" in href:
            categories.add(urljoin(TOP_URL, href))

    result = sorted(categories)

    print("[CATEGORY]", len(result))
    for x in result:
        print(x)

    return result


# -------------------------
# 全記事取得
# -------------------------

def get_articles():
    categories = get_categories()
    all_articles = []
    global_seen = set()

    for category in categories:
        print("[LIST]", category)

        soup = get_soup(category)
        articles = extract_articles_from_soup(soup, BASE_URL)

        for a in articles:
            if a["url"] in global_seen:
                continue
            global_seen.add(a["url"])
            all_articles.append(a)

    print("[ARTICLES]", len(all_articles))
    return all_articles


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
            "content":
                "【UNITED ONLINE PLUS更新】\n"
                f"{article['title']}\n"
                f"{article['url']}"
        },
        timeout=10
    ).raise_for_status()


# -------------------------
# main
# -------------------------

def main():
    print("=== START UNITED ONLINE PLUS ===")

    seen = load_seen()
    print("[SEEN]", len(seen))

    articles = get_articles()

    new_articles = [
        a for a in articles
        if a["url"] not in seen
    ]

    print("[NEW]", len(new_articles))

    # 初回は登録のみ
    if not seen and new_articles:
        print("[INIT] register only")
        for a in new_articles:
            seen.add(a["url"])
        save_seen(seen)
        return

    for article in reversed(new_articles):
        try:
            print("[SEND]", article["title"])
            send_discord(article)
            seen.add(article["url"])
        except Exception as e:
            print("[ERROR]", e)

    save_seen(seen)

    print("=== DONE UNITED ONLINE PLUS ===")


if __name__ == "__main__":
    main()
