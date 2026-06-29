import json
import os
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://jefunited.co.jp"

TOP_URL = (
    "https://jefunited.co.jp/my/uoplus/"
)

SEEN_FILE = (
    "seen_united_online_plus.json"
)


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}





# -------------------------
# seen
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
# HTML取得
# -------------------------

def fetch_html(url):

    print(
        "[FETCH]",
        url
    )


    r = requests.get(

        url,

        headers=HEADERS,

        timeout=10

    )


    print(
        "[STATUS]",
        r.status_code
    )


    r.raise_for_status()


    return BeautifulSoup(

        r.text,

        "html.parser"

    )







# -------------------------
# カテゴリ取得
# -------------------------

def fetch_category_urls():


    print(
        "[CATEGORY] fetching"
    )


    soup = fetch_html(

        TOP_URL

    )


    urls = set()



    for a in soup.find_all(

        "a",

        href=True

    ):


        url = urljoin(

            TOP_URL,

            a["href"]

        ).split("?")[0]



        # list?c=xxxだけ

        if "/my/uoplus/list" in a["href"]:


            urls.add(

                urljoin(
                    TOP_URL,
                    a["href"]
                )

            )





    result = sorted(

        urls

    )


    print(

        "[CATEGORY]",

        len(result)

    )


    for x in result:

        print(
            x
        )


    return result







# -------------------------
# 記事取得
# -------------------------

def fetch_articles():


    articles = []


    categories = fetch_category_urls()



    for category in categories:


        print(

            "[LIST]",

            category

        )


        soup = fetch_html(

            category

        )




        # 全タグ探索

        for tag in soup.find_all(True):


            for attr in [

                "href",

                "data-href",

                "data-url"

            ]:


                value = tag.get(attr)



                if not value:

                    continue




                url = urljoin(

                    category,

                    value

                ).split("?")[0]





                if "/my/uoplus/detail/" not in url:

                    continue




                # メルマガ除外

                if url.endswith(

                    "/detail/c/mail/"

                ):

                    continue






                title = tag.get_text(

                    " ",

                    strip=True

                )



                if not title:


                    title = (

                        "UNITED ONLINE PLUS"

                    )






                articles.append(

                    {

                        "url": url,

                        "title": title

                    }

                )








    # URL重複排除

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

        "[ARTICLES]",

        len(result)

    )


    print(

        result[:10]

    )


    return result







# -------------------------
# Discord
# -------------------------

def send_discord(article):


    webhook = os.environ.get(

        "UNITEDONLINEPLUS_WEBHOOK"

    )


    if not webhook:


        raise Exception(

            "UNITEDONLINEPLUS_WEBHOOK missing"

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


    r.raise_for_status()







# -------------------------
# main
# -------------------------

def main():


    print(

        "=== START UNITED ONLINE PLUS ==="

    )



    seen = load_seen()



    print(

        "[SEEN]",

        len(seen)

    )





    articles = fetch_articles()




    new_articles = [

        a

        for a in articles

        if a["url"] not in seen

    ]





    print(

        "[NEW]",

        len(new_articles)

    )






    # 初回登録

    if not seen and new_articles:


        print(

            "[INIT] register"

        )


        for a in new_articles:

            seen.add(

                a["url"]

            )



        save_seen(seen)

        return






    for article in reversed(new_articles):


        try:


            print(

                "[SEND]",

                article["title"]

            )


            send_discord(article)



            seen.add(

                article["url"]

            )



        except Exception as e:


            print(

                "[ERROR]",

                e

            )







    save_seen(seen)



    print(

        "=== DONE UNITED ONLINE PLUS ==="

    )






if __name__ == "__main__":


    main()
