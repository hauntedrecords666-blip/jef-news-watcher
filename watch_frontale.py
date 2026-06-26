import json
import os
import re
import requests
from bs4 import BeautifulSoup


NEWS_URL = "https://www.frontale.co.jp/info/"
BASE_URL = "https://www.frontale.co.jp"

SEEN_FILE = "seen_frontale.json"


def load_seen():

    try:

        with open(
            SEEN_FILE,
            encoding="utf-8"
        ) as f:

            return set(json.load(f))

    except Exception:

        return set()



def save_seen(seen):

    with open(
        SEEN_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            list(seen),
            f,
            ensure_ascii=False,
            indent=2
        )



def get_articles():

    try:

        r = requests.get(
            NEWS_URL,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

    except Exception:

        return []


    if r.status_code != 200:

        return []


    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    articles = []


    for a in soup.find_all(
        "a",
        href=True
    ):


        url = a["href"]


        # 川崎公式ニュース記事
        # 年月に依存しない
        if not re.search(
            r"/info/\d{4}/\d{2}/.*\.html$",
            url
        ):

            continue



        # 相対URLを絶対URL化

        if url.startswith("/"):

            url = BASE_URL + url



        title = a.get_text(
            " ",
            strip=True
        )


        if not title:

            continue



        articles.append(
            {
                "url": url,
                "title": title
            }
        )



    return articles




seen = load_seen()


articles = get_articles()



new_articles = [
    article
    for article in articles
    if article["url"] not in seen
]



# 新着通知

for article in reversed(new_articles):


    try:

        requests.post(
            os.environ["FRONTALE_WEBHOOK"],
            json={
                "content":
                f"【川崎フロンターレNEWS更新】\n"
                f"{article['title']}\n"
                f"{article['url']}"
            },
            timeout=10
        )


    except Exception:

        pass



    seen.add(
        article["url"]
    )



save_seen(seen)
