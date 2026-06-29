import json
import os
import re
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







def fetch_html(url):

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    r.raise_for_status()

    return r.text







def fetch_category_urls():


    html = fetch_html(
        TOP_URL
    )


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    urls = set()



    for a in soup.find_all(
        "a",
        href=True
    ):


        href = a["href"]


        if "/my/uoplus/list?c=" in href:


            urls.add(
                urljoin(
                    TOP_URL,
                    href
                )
            )



    return sorted(urls)









def fetch_articles():


    articles = []



    categories = fetch_category_urls()



    print(
        "[CATEGORY]",
        len(categories)
    )



    for category in categories:


        print(
            "[LIST]",
            category
        )


        html = fetch_html(
            category
        )


        soup = BeautifulSoup(
            html,
            "html.parser"
        )



        # 全HTMLからdetail URL抽出

        matches = re.findall(

            r'(?:"|\'|=)([^"\']*detail[^"\']+)',

            html

        )



        for m in matches:


            url = urljoin(
                category,
                m
            )



            if "/my/uoplus/detail/" not in url:

                continue



            if url.endswith(
                "/detail/c/mail/"
            ):

                continue



            articles.append(

                {
                    "url": url.split("?")[0],
                    "title": ""
                }

            )





    result = []

    exists = set()



    for a in articles:


        if a["url"] in exists:

            continue



        exists.add(
            a["url"]
        )


        result.append(a)





    print(
        "[ARTICLES]",
        len(result)
    )


    print(
        result[:10]
    )


    return result







def fetch_title(url):

    try:

        html = fetch_html(
            url
        )


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        h1 = soup.find("h1")


        if h1:

            return h1.get_text(
                " ",
                strip=True
            )


        title = soup.find(
            "title"
        )


        if title:

            return title.get_text(
                " ",
                strip=True
            )


    except:

        pass



    return "UNITED ONLINE PLUS"







def send_discord(article):


    webhook = os.environ.get(
        "UNITEDONLINEPLUS_WEBHOOK"
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



    for a in articles:

        if not a["title"]:

            a["title"] = fetch_title(
                a["url"]
            )





    new_articles = [

        a

        for a in articles

        if a["url"] not in seen

    ]



    print(
        "[NEW]",
        len(new_articles)
    )





    if not seen and new_articles:


        for a in new_articles:

            seen.add(
                a["url"]
            )


        save_seen(seen)

        return






    for a in reversed(new_articles):


        send_discord(a)

        seen.add(
            a["url"]
        )





    save_seen(seen)



    print(
        "=== DONE UNITED ONLINE PLUS ==="
    )






if __name__ == "__main__":

    main()
