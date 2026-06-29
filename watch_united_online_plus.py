import json
import os
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin



LIST_URL = "https://jefunited.co.jp/my/uoplus/"

BASE_URL = "https://jefunited.co.jp"

SEEN_FILE = "seen_united_online_plus.json"


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
# 一覧取得
# -------------------------

def fetch_list():


    print("[LIST] fetching...")


    r = requests.get(

        LIST_URL,

        headers=HEADERS,

        timeout=10

    )


    print(
        "[LIST] status:",
        r.status_code
    )


    r.raise_for_status()



    soup = BeautifulSoup(

        r.text,

        "html.parser"

    )



    articles = []



    for a in soup.select(
        "a[href]"
    ):



        href = a.get(
            "href"
        )



        if not href:

            continue



        url = urljoin(

            LIST_URL,

            href

        ).split("?")[0]



        # UO+記事っぽいURLのみ
        # 実際のURL確認用に広め

        if "/my/uoplus/" not in url:

            continue



        if url == LIST_URL:

            continue



        title = a.get_text(

            " ",

            strip=True

        )



        articles.append(

            {

                "url": url,

                "title": title

            }

        )



    result = []

    seen_urls = set()



    for a in articles:


        if a["url"] in seen_urls:

            continue



        seen_urls.add(

            a["url"]

        )


        result.append(a)




    print(

        "[LIST] articles:",

        len(result)

    )


    print(

        "[LIST] sample:",

        result[:3]

    )



    return result







# -------------------------
# Discord送信
# -------------------------

def send_discord(article):


    webhook = os.environ.get(

        "UNITEDONLINEPLUS_WEBHOOK"

    )


    if not webhook:

        raise Exception(

            "UNITEDONLINEPLUS_WEBHOOK missing"

        )



    print(

        "[DISCORD] send:",

        article["url"]

    )



    r = requests.post(

        webhook,

        json={

            "content":

                "【UNITED ONLINE PLUS更新】\n"

                f"{article['title']}\n"

                f"{article['url']}"

        },

        timeout=10

    )



    print(

        "[DISCORD] status:",

        r.status_code

    )


    r.raise_for_status()







# -------------------------
# main
# -------------------------

def main():


    print(

        "=== START UO+ ==="

    )



    seen = load_seen()



    print(

        "[SEEN] size:",

        len(seen)

    )



    articles = fetch_list()



    new_articles = [

        a

        for a in articles

        if a["url"] not in seen

    ]



    print(

        "[NEW]",

        len(new_articles)

    )





    # 初回は通知しない

    if not seen and new_articles:


        print(

            "[INIT] skip"

        )


        for a in new_articles:

            seen.add(

                a["url"]

            )


        save_seen(seen)

        return






    for article in reversed(new_articles):


        try:


            send_discord(article)



            seen.add(

                article["url"]

            )



        except Exception as e:


            print(

                "send error:",

                e

            )




    save_seen(seen)



    print(

        "=== DONE UO+ ==="

    )






if __name__ == "__main__":

    main()
