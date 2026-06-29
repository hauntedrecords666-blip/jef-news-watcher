LIST_URL = "https://jefunited.co.jp/my/uoplus/"
SEEN_FILE = "seen_united_online_plus.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


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


    for item in soup.select(
        ".l-plus__item"
    ):


        a = item.find(
            "a",
            href=True
        )


        if not a:
            continue


        url = urljoin(
            LIST_URL,
            a["href"]
        )


        if "/my/uoplus/detail/" not in url:

            continue


        title = item.get_text(
            " ",
            strip=True
        )


        articles.append(
            {
                "url": url,
                "title": title
            }
        )


    print(
        "[LIST] articles:",
        len(articles)
    )


    print(
        "[LIST] sample:",
        articles[:5]
    )


    return articles
