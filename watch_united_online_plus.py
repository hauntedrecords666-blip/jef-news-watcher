import json
import os
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin



LIST_URL = (
    "https://jefunited.co.jp/my/uoplus/"
)

SEEN_FILE = (
    "seen_united_online_plus.json"
)


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

            return set(
                json.load(f)
            )


    except FileNotFoundError:

        return set()





def save_seen(seen):

    with open(
        SEEN_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            sorted(
                list(seen)
            ),

            f,

            ensure_ascii=False,

            indent=2

        )








# -------------------------
# 一覧取得
# -------------------------

def fetch_list():


    print(
        "[LIST] fetching..."
    )


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




    # UO+カード

    items = soup.select(

        ".l-plus__item"

    )



    print(

        "[LIST] cards:",

        len(items)

    )





    for item in items:



        link = item.find(

            "a",

            href=True

        )



        if not link:

            continue




        href = link.get(

            "href"

        )



        if "/my/uoplus/detail/" not in href:

            continue




        url = urljoin(

            LIST_URL,

            href

        ).split("?")[0]






        # 固定ページ除外

        if url.endswith(

            "/detail/c/mail/"

        ):

            continue






        title = item.get_text(

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







    # 重複排除

    result = []

    exists = set()



    for article in articles:



        if article["url"] in exists:

            continue



        exists.add(

            article["url"]

        )


        result.append(

            article

        )





    print(

        "[LIST] articles:",

        len(result)

    )



    print(

        "[LIST] sample:",

        result[:5]

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

        article["title"]

    )




    res = requests.post(

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

        res.status_code

    )



    res.raise_for_status()








# -------------------------
# main
# -------------------------

def main():


    print(

        "=== START UNITED ONLINE PLUS ==="

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

        "[NEW]:",

        len(new_articles)

    )






    # 初回登録

    if not seen and new_articles:


        print(

            "[INIT] skip notification"

        )



        for article in new_articles:


            seen.add(

                article["url"]

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

                "[SEND ERROR]",

                e

            )







    save_seen(seen)



    print(

        "=== DONE UNITED ONLINE PLUS ==="

    )






if __name__ == "__main__":

    main()
