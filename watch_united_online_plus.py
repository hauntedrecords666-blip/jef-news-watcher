import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE = "https://jefunited.co.jp"
SEEN_FILE = "seen_united_online_plus.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TARGET_CATEGORIES = [
    "article",
    "book",
    "column",
    "download",
    "movieplus",
    "quickreport",
    "video"
]


# -------------------------
# seen
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
# fetch
# -------------------------

def fetch_html_requests(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.text


def fetch_html_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        browser.close()
        return html


# -------------------------
# 記事判定（ここが本体）
# -------------------------

def is_article(url: str):
    if "/my/uoplus/detail/c/" in url:
        return True

    if "youtu.be" in url:
        return True

    return False


def is_noise(url: str):
    noise = [
        "/law",
        "/term",
        "/service",
        "/privacypolicy"
    ]
    return any(n in url for n in noise)


# -------------------------
# 抽出
# -------------------------

def extract_articles(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    results = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        url = urljoin(base_url, href).split("?")[0]

        if is_noise(url):
            continue

        if not is_article(url):
            continue

        if url in seen:
            continue
        seen.add(url)

        title = a.get_text(" ", strip=True)
        if not title:
            title = "UNITED ONLINE PLUS"

        results.append({
            "url": url,
            "title": title
        })

    return results


# -------------------------
# 全カテゴリ取得
# -------------------------

def fetch_all_articles():
    all_articles = []

    for c in TARGET_CATEGORIES:
        url = f"{BASE}/my/uoplus/list?c={c}"

        html = fetch_html_requests(url)
        articles = extract_articles(html, url)

        # JS崩れ対策フォールバック
        if len(articles) == 0:
            html = fetch_html_playwright(url)
            articles = extract_articles(html, url)

        all_articles.extend(articles)

    # 重複排除
    uniq = {}
    for a in all_articles:
        uniq[a["url"]] = a

    return list(uniq.values())


# -------------------------
# Discord
# -------------------------

def send_discord(article):
    webhook = os.environ.get("UNITEDONLINEPLUS_WEBHOOK")
    if not webhook:
        raise Exception("missing webhook")

    requests.post(
        webhook,
        json={
            "content": f"【UNITED ONLINE PLUS更新】\n{article['title']}\n{article['url']}"
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

    articles = fetch_all_articles()
    print("[ARTICLES]", len(articles))

    new_articles = [a for a in articles if a["url"] not in seen]
    print("[NEW]", len(new_articles))

    # 初回は登録のみ
    if not seen and new_articles:
        for a in new_articles:
            seen.add(a["url"])
        save_seen(seen)
        return

    for a in reversed(new_articles):
        try:
            print("[SEND]", a["title"])
            send_discord(a)
            seen.add(a["url"])
        except Exception as e:
            print("[ERROR]", e)

    save_seen(seen)

    print("=== DONE UNITED ONLINE PLUS ===")


if __name__ == "__main__":
    main()
