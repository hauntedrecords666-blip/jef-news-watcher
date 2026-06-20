import json
import os
import requests
from bs4 import BeautifulSoup


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
        json.dump(
            list(seen),
            f,
            ensure_ascii=False,
            indent=2
        )


def get_number(url):
    try:
        return int(
            url.rstrip("/").split("/")[-1]
        )
    except:
        return None


def get_latest_seen(seen):

    nums = []

    for url in seen:
        n = get_number(url)

        if n:
            nums.append(n)

    if nums:
        return max(nums)

    # 初回基準
    return 5208



def fetch_news(number):

    url = BASE_URL + str(number)

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


    # リダイレクト・存在しないページ対策
    if r.url.rstrip("/") != url:
        return None


    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    # 本物の記事判定
    h1 = soup.find("h1")

    if not h1:
        return None


    title = h1.get_text(
        " ",
        strip=True
    )


    if not title:
        return None


    title = title.replace(
        "｜ニュース｜ジェフユナイテッド市原・千葉 公式ウェブサイト",
        ""
    )


    return {
        "url": url,
        "title": title.strip()
    }



seen = load_seen()


latest = get_latest_seen(seen)


# 前後を見る
start = latest - 50
end = latest + 101


articles = []


for number in range(start, end):

    if number <= 0:
        continue


    article = fetch_news(number)


    if article:
        articles.append(article)



# 未通知だけ
new_articles = [
    a for a in articles
    if a["url"] not in seen
]



# 初回だけは大量通知しない
if not seen and new_articles:

    # 最新だけを基準登録
    latest_article = max(
        new_articles,
        key=lambda x: get_number(x["url"])
    )

    seen.add(
        latest_article["url"]
    )


else:

    # 番号順
    new_articles.sort(
        key=lambda x: get_number(x["url"])
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
