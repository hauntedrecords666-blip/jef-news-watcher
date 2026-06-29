from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://jefunited.co.jp"


def fetch_showcase():
    urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE, wait_until="domcontentloaded")

        # ここ重要：networkidleじゃなくDOM後すぐ取る
        html = page.content()

        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    showcase = soup.select_one("#showcase")
    if not showcase:
        return []

    for item in showcase.select(".swiper-slide"):
        a = item.find("a")

        if not a:
            continue

        # hrefが無い場合もあるので属性総チェック
        href = a.get("href") or a.get("data-href")

        if not href:
            continue

        url = urljoin(BASE, href).split("?")[0]

        if "/matches/" in url or "youtu.be" in url:
            urls.add(url)

    return sorted(urls)
