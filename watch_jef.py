import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

LIST_URL = "https://jefunited.co.jp/news/"
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

    urls = set()

    for a in soup.select("a[href]"):
        href = a.get("href")

        if not href:
            continue

        if "/news/detail/" in href:
            full_url = urljoin(LIST_URL, href)
            urls.add(full_url.split("?")[0])

    return list(urls)


def fetch_detail(url):
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
    except Exception as e:
        print("request error:", url, e)
        return None

    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    title_tag = soup.find("h1") or soup.find("title")
    if not title_tag:
        return None

    title = title_tag.get_text(" ", strip=True)

    title = title.replace(
        "｜ニュース｜ジェフユナイテッド市原・千葉 公式ウェブサイト",
        ""
    ).strip()

    return {
        "url": url,
        "title": title
    }


def send_discord(article):
    res = requests.post(
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

    print("discord status:", res.status_code)


def main():
    seen = load_seen()

    urls = fetch_list()

    print("fetched:", len(urls))
    print("seen:", len(seen))

    new_urls = set(urls) - seen

    print("new:", len(new_urls))

    if not seen and new_urls:
        seen.update(new_urls)
        save_seen(seen)
        print("initial run skip")
        return

    articles = []

    for url in new_urls:
        article = fetch_detail(url)
        if article:
            articles.append(article)

    for article in articles:
        send_discord(article)
        seen.add(article["url"])

    save_seen(seen)
    print("done")


if __name__ == "__main__":
    main()