import json
import os
import requests
from bs4 import BeautifulSoup


NEWS_URL = "https://blackrams-tokyo.com/news/index.html"
BASE_URL = "https://blackrams-tokyo.com"

SEEN_FILE = "seen_blackrams.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}



# -------------------------
# seen管理
# -------------------------
def load_seen():

    try:

        with open(
            SEEN_FILE,
            encoding="utf-8"
        ) as f:

            return set(json.load(f))


    except FileNotFoundError:

        return set()



def save_seen(seen):

    with open(
        SEEN_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            sorted(list(seen)),
            f,
            ensure_ascii=False,
            indent=2
        )



# -------------------------
# 記事取得
# -------------------------
def get_articles():


    r = requests.get(
        NEWS_URL,
        headers=HEADERS,
        timeout=10
    )


    r.raise_for_status()



    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )



    articles = []



    # ニュース一覧部分だけ取得
    for dd in soup.select(
        "dl.infoIndex dd"
    ):


        a = dd.find(
            "a",
            href=True
        )


        if not a:

            continue



        url = a["href"]



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



# -------------------------
# OG画像取得
# -------------------------
def get_og_image(url):


    r = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )


    r.raise_for_status()



    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )



    og = soup.find(
        "meta",
        property="og:image"
    )



    if og:

        return og.get("content")



    return None



# -------------------------
# Discord送信
# -------------------------
def send_discord(article):


    webhook = os.environ.get(
        "BLACKRAMS_WEBHOOK"
    )


    if not webhook:

        raise Exception(
            "BLACKRAMS_WEBHOOK missing"
        )



    image = get_og_image(
        article["url"]
    )



    embed = {

        "title": article["title"],

        "url": article["url"],

        "description":
            "ブラックラムズ東京 公式NEWS"

    }



    if image:

        embed["image"] = {

            "url": image

        }



    res = requests.post(

        webhook,

        json={

            "embeds": [

                embed

            ]

        },

        timeout=10

    )



    res.raise_for_status()



# -------------------------
# main
# -------------------------
def main():


    seen = load_seen()



    articles = get_articles()



    print(
        "articles:",
        len(articles)
    )



    new_articles = [

        a

        for a in articles

        if a["url"] not in seen

    ]



    print(
        "new:",
        len(new_articles)
    )



    for article in reversed(new_articles):


        print(
            "sending:",
            article["title"]
        )



        send_discord(article)



        seen.add(
            article["url"]
        )



    save_seen(seen)



    print(
        "done"
    )



if __name__ == "__main__":

    main()
