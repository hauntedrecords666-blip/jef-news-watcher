import json
import os
import requests
from bs4 import BeautifulSoup


NEWS_URL = "https://blackrams-tokyo.com/news/index.html"
BASE_URL = "https://blackrams-tokyo.com"

SEEN_FILE = "seen_blackrams.json"



def load_seen():

    try:
        with open(
            SEEN_FILE,
            encoding="utf-8"
        ) as f:
            return set(json.load(f))

    except:
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

    except:

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


        if "/news/" not in url:
            continue


        if not url.endswith(".html"):
            continue


        if url.endswith("index.html"):
            continue


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




def get_og_image(url):

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





seen = load_seen()


articles = get_articles()



new_articles = [
    a
    for a in articles
    if a["url"] not in seen
]



for article in reversed(new_articles):


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



    requests.post(

        os.environ["BLACKRAMS_WEBHOOK"],

        json={

            "embeds": [
                embed
            ]

        },

        timeout=10

    )



    seen.add(
        article["url"]
    )



save_seen(seen)
