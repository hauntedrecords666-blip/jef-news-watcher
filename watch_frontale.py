import json
import os
import re
import requests

from bs4 import BeautifulSoup


NEWS_URL = "https://www.frontale.co.jp/info/"
BASE_URL = "https://www.frontale.co.jp"

SEEN_FILE = "seen_frontale.json"


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
# タイトル取得
# -------------------------

def get_title(url):

    try:

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


        title = soup.find("title")


        if title:

            text = title.get_text(
                " ",
                strip=True
            )

            return text.replace(
                " | 川崎フロンターレ",
                ""
            )


    except Exception as e:

        print(
            "title error:",
            url,
            e
        )


    return "川崎フロンターレ NEWS"





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



        # フロンターレ記事URLのみ
        if not re.search(
            r"/info/\d{4}/\d{4}_\d+\.html$",
            url
        ):

            continue



        title = a.get_text(
            " ",
            strip=True
        )



        if not title:

            title = get_title(url)



        articles.append(
            {
                "url": url,
                "title": title
            }
        )



    # URL重複排除

    result = []

    seen_urls = set()



    for article in articles:


        if article["url"] in seen_urls:

            continue


        seen_urls.add(
            article["url"]
        )


        result.append(
            article
        )



    return result






# -------------------------
# Discord送信
# -------------------------

def send_discord(article):


    webhook = os.environ.get(
        "FRONTALE_WEBHOOK"
    )



    if not webhook:

        raise Exception(
            "FRONTALE_WEBHOOK missing"
        )



    payload = {

        "content":
            "【川崎フロンターレNEWS更新】\n"
            f"{article['title']}\n"
            f"{article['url']}"

    }



    r = requests.post(

        webhook,

        json=payload,

        timeout=10

    )


    r.raise_for_status()





# -------------------------
# main
# -------------------------

def main():


    seen = load_seen()



    articles = get_articles()



    print(
        "DEBUG articles:",
        len(articles)
    )



    new_articles = [

        a for a in articles

        if a["url"] not in seen

    ]



    print(
        "DEBUG new:",
        len(new_articles)
    )



    for article in reversed(new_articles):


        print(
            "sending:",
            article["title"],
            article["url"]
        )



        try:

            send_discord(article)


            seen.add(
                article["url"]
            )


        except Exception as e:


            print(
                "send failed:",
                e
            )



    save_seen(seen)



    print(
        "done"
    )





if __name__ == "__main__":

    main()
