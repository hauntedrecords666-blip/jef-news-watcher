import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://jefunited.co.jp"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# -------------------------
# SHOWCASE判定
# -------------------------

def is_noise(url: str):
    return any(x in url for x in [
        "/law",
        "/term",
        "/service",
        "/privacypolicy"
    ])


def is_article(url: str):
    # 記事として扱うのはこの2種類だけ
    return (
        "/matches/contents/" in url
        or "/matches/stats/" in url
        or "/my/uoplus/detail/" in url
    )


# -------------------------
# SHOWCASE取得
# -------------------------

def fetch_showcase_articles():
    r = requests.get(BASE, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    showcase = soup.select_one("#showcase")
    if not showcase:
        return []

    urls = set()

    for a in showcase.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue

        url = urljoin(BASE, href).split("?")[0]

        if is_noise(url):
            continue

        if not is_article(url):
            continue

        urls.add(url)

    return sorted(urls)


# -------------------------
# main
# -------------------------

def main():
    print("=== SHOWCASE SCRAPER START ===")

    urls = fetch_showcase_articles()

    print("[ARTICLES]", len(urls))
    for u in urls:
        print(u)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
