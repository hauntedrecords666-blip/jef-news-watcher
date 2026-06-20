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


def get_latest_number(seen):

    nums = []

    for url in seen:
        try:
            nums.append(
                int(url.rstrip("/").split("/")[-1])
            )
        except:
            pass

    if nums:
        return max(nums)

    # 初回だけ現在付近を探す
    return 5200


def get_article(number):

    url = BASE + str(number)

    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

    except:
        return None


    if r.status_code != 200:
        return None


    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    title = None


    # h1優先
    h1 = soup.find("h1")

    if h1:
        title = h1.get_text(
            " ",
            strip=True
        )


    # fallback
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


latest = get_latest_number(seen)


# 最新番号から未来100件を見る
check_numbers = range(
    latest + 1,
    latest + 101
)


articles = []


for number in check_numbers:

    article = get_article(number)

    if article:
        articles.append(article)



new_articles = [
    a
    for a in articles
    if a["url"] not in seen
]


if new_articles:

    # 古い記事から通知
    for article in reversed(new_articles):

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


else:

    # 初回や変更なしでも保存
    save_seen(seen)
