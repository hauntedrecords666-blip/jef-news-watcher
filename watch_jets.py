import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


LIST_URL = "https://chibajets.jp/news/"
BASE_URL = "https://chibajets.jp"

SEEN_FILE = "seen_jets.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}



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
            sorted(list(seen)),
            f,
            ensure_ascii=False,
            indent=2
        )



def fetch_list():

    try:

        r = requests.get(
            LIST_URL,
            headers=HEADERS,
            timeout=10
        )

        if r.status_code != 200:

            return []

    except:

        return []


    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    articles = []


    for a in soup.select("a[href]"):


        href = a.get("href")


        if not href:

            continue



        if "/news/detail/" not in href:

            continue



        url = urljoin(
            LIST_URL,
            href
        )


        url = url.split("?")[0]


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




def send_discord(article):

    try:

        requests.post(
            os.environ["JETS_WEBHOOK"],
            json={
                "content":
                f"【千葉ジェッツNEWS更新】\n"
                f"{article['title']}\n"
                f"{article['url']}"
            },
            timeout=10
        )


    except Exception as e:

        print(
            "discord error:",
            e
        )




def main():

    seen = load_seen()


    articles = fetch_list()



    new_articles = [

        a

        for a in articles

        if a["url"] not in seen

    ]



    # 初回暴発防止

    if not seen and new_articles:

        for a in new_articles:

            seen.add(
                a["url"]
            )


        save_seen(seen)

        print("initial skip")

        return




    for article in reversed(new_articles):


        send_discord(
            article
        )


        seen.add(
            article["url"]
        )



    save_seen(seen)



if __name__ == "__main__":

    main()
