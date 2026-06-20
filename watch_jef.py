import json
import os
import requests
from bs4 import BeautifulSoup


BASE = "https://jefunited.co.jp/news/detail/"
SEEN_FILE = "seen.json"


def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            list(seen),
            f,
            ensure_ascii=False,
            indent=2
        )


def extract_number(url):
    try:
        return int(
            url.rstrip("/").split("/")[-1]
        )
    except:
        return None


def get_base_number(seen):

    numbers = []

    for url in seen:
        n = extract_number(url)

        if n:
            numbers.append(n)

    if numbers:
        return max(numbers)

    # 初回
    return 5200



def get_article(number):

    url = BASE + str(number)

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

    except:
        return None


    if response.status_code != 200:
        return None


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    title = None


    h1 = soup.find("h1")

    if h1:
        title = h1.get_text(
            " ",
            strip=True
        )


    if not title and soup.title:
        title = soup.title.text


    if not title:
        title = f"NEWS {number}"


    title = title.replace(
        "｜ニュース｜ジェフユナイテッド市原・千葉 公式ウェブサイト",
        ""
    )


    return {
        "url": url,
        "title": title.strip()
    }



seen = load_seen()


base_number = get_base_number(seen)


# 既存番号の前後を見る
check_range = range(
    base_number - 50,
    base_number + 101
)


articles = []


for number in check_range:

    if number <= 0:
        continue

    article = get_article(number)

    if article:
        articles.append(article)



new_articles = [
    article
    for article in articles
    if article["url"] not in seen
]


if new_articles:

    # 古い番号順
    new_articles.sort(
        key=lambda x: extract_number(x["url"])
    )


    for article in new_articles:

        requests.post(
            os.environ["DISCORD_WEBHOOK"],
            json={
                "content":
                f"【ジェフNEWS更新】\n"
                f"{article['title']}\n"
                f"{article['url']}"
            },
            timeout=10
        )


        seen.add(
            article["url"]
        )


save_seen(seen)
