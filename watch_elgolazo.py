import json
import os
import re
import requests

from bs4 import BeautifulSoup


NEWS_URL = (
    "https://elgolazo.jp/products/list"
    "?category_id=1084"
)

BASE_URL = "https://elgolazo.jp"

SEEN_FILE = "seen_elgolazo.json"


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
# 商品取得
# -------------------------

def get_products():


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



    products = []



    for a in soup.select(
        "a[href]"
    ):


        href = a.get("href")


        if not href:

            continue



        if href.startswith("/"):

            url = BASE_URL + href

        else:

            url = href



        # 商品詳細URL想定
        if not re.search(
            r"/products/detail/\d+",
            url
        ):

            continue



        title = a.get_text(
            " ",
            strip=True
        )



        if not title:

            title = get_title(url)



        products.append(
            {
                "url": url,
                "title": title
            }
        )



    # 重複排除

    result = []

    seen_urls = set()


    for p in products:


        if p["url"] in seen_urls:

            continue


        seen_urls.add(
            p["url"]
        )


        result.append(p)



    return result





# -------------------------
# 詳細タイトル取得
# -------------------------

def get_title(url):

    try:

        r = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )


        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )


        title = soup.find("title")


        if title:

            return title.get_text(
                " ",
                strip=True
            )


    except Exception as e:

        print(
            "title error",
            e
        )


    return "EL GOLAZO 商品"





# -------------------------
# main
# -------------------------

def main():


    seen = load_seen()


    products = get_products()



    print(
        "DEBUG products:",
        len(products)
    )



    new_products = [

        p for p in products

        if p["url"] not in seen

    ]



    print(
        "DEBUG new:",
        len(new_products)
    )



    for p in reversed(new_products):


        print(
            "NEW:",
            p["title"],
            p["url"]
        )



        seen.add(
            p["url"]
        )



    save_seen(seen)



    print(
        "done"
    )




if __name__ == "__main__":

    main()
