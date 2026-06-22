import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://jefunited.co.jp/news/detail/"
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

    # タイトル取得（h1がダメでもtitleで救済）
    title_tag = soup.find("h1")
    if not title_tag:
        title_tag = soup.find("title")

    if not title_tag:
        return None

    title = title_tag.get_text(" ", strip=True)

    # ノイズ削除
    title = title.replace(
        "｜ニュース｜ジェフユナイテッド市原・千葉 公式ウェブサイト",
        ""
    ).strip()

    return {
        "url": url,
        "title": title
    }


def scan_range(latest_seen_num, range_size=120):
    articles = []

    start = latest_seen_num + 1
    end = latest_seen_num + range_size

    for num in range(start, end):
        url = BASE_URL + str(num)
        article = fetch_detail(url)

        if article:
            articles.append(article)

    return articles


def get_latest_seen(seen):
    nums = []

    for url in seen:
        try:
            nums.append(int(url.rstrip("/").split("/")[-1]))
        except:
            pass

    return max(nums) if nums else 5200


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

    print("discord status:", res.status_code, res.text)


def main():
    seen = load_seen()

    latest = get_latest_seen(seen)

    print("latest seen:", latest)

    articles = scan_range(latest)

    print("fetched:", len(articles))

    new_articles = [
        a for a in articles
        if a["url"] not in seen
    ]

    print("new:", len(new_articles))

    # 初回暴発防止
    if not seen and new_articles:
        seen.add(new_articles[-1]["url"])
        save_seen(seen)
        print("initial run skip")
        return

    for article in sorted(new_articles, key=lambda x: int(x["url"].split("/")[-1])):
        send_discord(article)
        seen.add(article["url"])

    save_seen(seen)
    print("done")


if __name__ == "__main__":
    main()