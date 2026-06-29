import requests
import json

BASE = "https://jefunited.co.jp"

API = BASE + "/my/uoplus/list-api"
PAGER_API = BASE + "/my/uoplus/list-Pager-api"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": BASE + "/my/uoplus/"
}


def fetch_page(page=1):
    params = {
        "page": page
    }

    r = requests.get(
        API,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    r.raise_for_status()
    return r.json()


def extract_articles(data):
    articles = []

    # 構造ゆらぎ対応
    candidates = (
        data.get("articles")
        or data.get("data")
        or data.get("result")
        or []
    )

    for a in candidates:
        url = a.get("url") or a.get("link")
        title = a.get("title") or a.get("name")

        if not url:
            continue

        if not url.startswith("http"):
            url = BASE + url

        articles.append({
            "url": url.split("?")[0],
            "title": title or "UNTITLED"
        })

    return articles


def fetch_all():
    all_articles = []
    page = 1

    while True:
        data = fetch_page(page)
        articles = extract_articles(data)

        if not articles:
            break

        all_articles.extend(articles)

        page += 1

        # 無限ループ防止
        if page > 20:
            break

    # 重複排除
    seen = set()
    result = []

    for a in all_articles:
        if a["url"] in seen:
            continue
        seen.add(a["url"])
        result.append(a)

    return result


def main():
    print("=== UO PLUS API SCRAPER ===")

    articles = fetch_all()

    print(f"[ARTICLES] {len(articles)}")

    for a in articles[:20]:
        print(a)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
