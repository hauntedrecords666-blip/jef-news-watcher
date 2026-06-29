import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://jefunited.co.jp"

CATEGORIES = [
    "/my/uoplus/list?c=article",
    "/my/uoplus/list?c=column",
    "/my/uoplus/list?c=book",
    "/my/uoplus/list?c=movieplus",
    "/my/uoplus/list?c=video",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_page(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def extract_articles(soup):
    results = []

    # aタグ総当たり（ここが正解）
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/my/uoplus/detail/" not in href:
            continue

        url = urljoin(BASE, href).split("?")[0]
        title = a.get_text(strip=True)

        if not title:
            title = "UNITED ONLINE PLUS"

        results.append({
            "url": url,
            "title": title
        })

    return results


def fetch_all():
    all_articles = []

    for path in CATEGORIES:
        url = BASE + path
        soup = fetch_page(url)

        articles = extract_articles(soup)
        all_articles.extend(articles)

    # dedupe
    seen = set()
    result = []

    for a in all_articles:
        if a["url"] in seen:
            continue
        seen.add(a["url"])
        result.append(a)

    return result


def main():
    print("=== UO PLUS HTML SCRAPER ===")

    articles = fetch_all()

    print("[ARTICLES]", len(articles))

    for a in articles[:20]:
        print(a)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
