import json
import os
import re
import asyncio

from playwright.async_api import async_playwright



LIST_URL = (
    "https://jefunited.co.jp/my/uoplus/"
)


SEEN_FILE = (
    "seen_united_online_plus.json"
)






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
# ブラウザ取得
# -------------------------

async def fetch_list():


    print(
        "[BROWSER] start"
    )



    async with async_playwright() as p:


        browser = await p.chromium.launch(

            headless=True

        )


        page = await browser.new_page(

            user_agent=
            "Mozilla/5.0"

        )



        await page.goto(

            LIST_URL,

            wait_until="networkidle",

            timeout=30000

        )



        # JS描画待ち

        await page.wait_for_timeout(

            3000

        )



        html = await page.content()



        await browser.close()






    from bs4 import BeautifulSoup



    soup = BeautifulSoup(

        html,

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




        if "/my/uoplus/detail/" not in href:

            continue





        url = (

            "https://jefunited.co.jp"

            + href

            if href.startswith("/")

            else href

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

        "[LIST]",

        len(result)

    )


    print(

        result[:5]

    )



    return result







# -------------------------
# Discord
# -------------------------

def send_discord(article):


    import requests



    webhook = os.environ.get(

        "UNITEDONLINEPLUS_WEBHOOK"

    )



    if not webhook:

        raise Exception(

            "missing webhook"

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

async def main():


    print(

        "=== START UNITED ONLINE PLUS ==="

    )


    seen = load_seen()



    print(

        "[SEEN]",

        len(seen)

    )



    articles = await fetch_list()





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

                "[SEND ERROR]",

                e

            )






    save_seen(seen)



    print(

        "=== DONE UNITED ONLINE PLUS ==="

    )






if __name__ == "__main__":


    asyncio.run(main())
