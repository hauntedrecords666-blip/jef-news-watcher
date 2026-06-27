import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


LIST_URL = "https://jefunited.co.jp/news/list"
BASE_DETAIL = "https://jefunited.co.jp/news/detail/"
SEEN_FILE = "seen.json"

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
# list取得
# -------------------------
def fetch_list():


    r = requests.get(
        LIST_URL,
        headers=HEADERS,
        timeout=10
    )


    r.raise_for_status()



    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    urls = set()



    for a in soup.select("a[href]"):


        href = a.get("href")


        if not href:

            continue



        if "/news/detail/" in href:


            full = urljoin(
                LIST_URL,
                href
            ).split("?")[0]


            urls.add(full)



    return list(urls)



# -------------------------
# ID抽出
# -------------------------
def extract_id(url):

    try:

        return int(
            url.rstrip("/").split("/")[-1]
        )


    except Exception:

        return None



# -------------------------
# 詳細取得
# -------------------------
def fetch_detail(url):


    r = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )



    # 存在しないIDは正常
    if r.status_code == 404:

        return None



    # その他HTTP異常
    r.raise_for_status()



    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )



    title = (

        soup.find("h1")

        or

        soup.find("title")

    )



    if not title:


        raise Exception(
            f"title not found: {url}"
        )



    text = title.get_text(
        " ",
        strip=True
    )



    text = text.replace(
        "｜ニュース｜ジェフユナイテッド市原・千葉 公式ウェブサイト",
        ""
    ).strip()



    return {

        "url": url,

        "title": text

    }



# -------------------------
# Discord送信
# -------------------------
def send_discord(article):


    webhook = os.environ.get(
        "DISCORD_WEBHOOK"
    )



    if not webhook:


        raise Exception(
            "DISCORD_WEBHOOK missing"
        )



    res = requests.post(

        webhook,

        json={

            "content":

                f"【ジェフNEWS更新】\n"

                f"{article['title']}\n"

                f"{article['url']}"

        },

        timeout=10

    )



    res.raise_for_status()



# -------------------------
# main
# -------------------------
def main():


    seen = load_seen()



    list_urls = fetch_list()



    ids = [

        extract_id(u)

        for u in list_urls

    ]


    ids = [

        i for i in ids

        if i is not None

    ]



    latest_list_id = max(ids) if ids else 0



    seen_ids = [

        extract_id(u)

        for u in seen

        if extract_id(u)

    ]



    latest_seen_id = (

        max(seen_ids)

        if seen_ids

        else 0

    )



    base = max(

        latest_list_id,

        latest_seen_id

    )



    print(
        "base id:",
        base
    )



    # 欠番確認用

    scan_range = range(

        base - 20,

        base + 50

    )



    candidates = []



    for i in scan_range:


        url = BASE_DETAIL + str(i)



        if url in seen:

            continue



        article = fetch_detail(url)



        if article:

            candidates.append(article)



    print(

        "found:",

        len(candidates)

    )



    # 初回暴発防止

    if not seen and candidates:


        for a in candidates:

            seen.add(
                a["url"]
            )


        save_seen(seen)


        print(
            "initial skip"
        )


        return



    # 通知

    for article in sorted(

        candidates,

        key=lambda x: extract_id(x["url"])

    ):


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
