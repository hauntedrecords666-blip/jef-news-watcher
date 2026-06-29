import json
import os
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


TOP_URL = "https://jefunited.co.jp/my/uoplus/"

SEEN_FILE = "seen_united_online_plus.json"

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





def get_soup(url):

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    r.raise_for_status()

    return BeautifulSoup(
        r.text,
        "html.parser"
    )





def get_categories():

    soup = get_soup(TOP_URL)

    result = set()


    for a in soup.find_all(
        "a",
        href=True
    ):

        href = a["href"]


        if "/my/uoplus/list?c=" in href:

            result.add(
                urljoin(
                    TOP_URL,
                    href
                )
            )


    return list(result)





def get_articles():


    articles = []


    for category in get_categories():


        print(
            "[LIST]",
            category
        )


        soup = get_soup(category)


        for a in soup.find_all(
            "a",
            href=True
        ):


            url = urljoin(
                category,
                a["href"]
            )


            url = url.split("?")[0]



            # UO+内ページだけ

            if not url.startswith(
                "https://jefunited.co.jp/my/uoplus/"
            ):

                continue



            # 一覧/固定ページ除外

            if "/list" in url:

                continue


            if url.endswith(
                "/my/uoplus/"
            ):

                continue


            if url.endswith(
                "/my/uoplus/about"
            ):

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





def send_discord(article):

    webhook = os.environ.get(
        "UNITEDONLINEPLUS_WEBHOOK"
    )


    requests.post(

        webhook,

        json={

            "content":

            "【UNITED ONLINE PLUS更新】\n"
            f"{article['title']}\n"
            f"{article['url']}"

        },

        timeout=10

    ).raise_for_status()





def main():

    print(
        "=== START UNITED ONLINE PLUS ==="
    )


    seen = load_seen()


    articles = get_articles()


    new = [

        a for a in articles

        if a["url"] not in seen

    ]


    print(
        "[NEW]",
        len(new)
    )



    if not seen:

        for a in articles:

            seen.add(
                a["url"]
            )

        save_seen(seen)

        return



    for a in reversed(new):

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
