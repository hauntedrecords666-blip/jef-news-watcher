import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

LIST_URL = "https://jefunited.co.jp/news/list"
BASE_DETAIL = "https://jefunited.co.jp/news/detail/"
SEEN_FILE = "seen.json"

HEADERS = {"User-Agent": "Mozilla/5.0"}


# -------------------------
# seen管理（正史）
# -------------------------
def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen)), f, ensure_ascii=False, indent=2)


# -------------------------
# list取得（補助）
# -------------------------
def fetch_list():
    try:
        r = requests.get(LIST_URL, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
    except:
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    urls = set()

    for a in soup.select("a[href]"):
        href = a.get("href")
        if not href:
            continue

        if "/news/detail/" in href:
            full = urljoin(LIST_URL, href).split("?")[0]
            urls.add(full)

    return list(urls)


# -------------------------
# ID抽出
# -------------------------
def extract_id(url):
    try:
        return int(url.rstrip("/").split("/")[-1])
    except:
        return None


# -------------------------
# 詳細取得
# -------------------------
def fetch_detail(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
    except:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1") or soup.find("title")
    if not title:
        return None

    text = title.get_text(" ", strip=True)

    text = text.replace(
        "｜ニュース｜ジェフユナイテッド市原・千葉 公式ウェブサイト",
        ""
    ).strip()

    return {"url": url, "title": text}


# -------------------------
# Discord送信
# -------------------------
def send_discord(article):
    try:
        res = requests.post(
            os.environ["DISCORD_WEBHOOK"],
            json={
                "content": f"【ジェフNEWS更新】\n{article['title']}\n{article['url']}"
            },
            timeout=10
        )
        print("discord:", res.status_code)
    except Exception as e:
        print("discord error:", e)


# -------------------------
# メインロジック
# -------------------------
def main():
    seen = load_seen()

    # ① list取得（補助）
    list_urls = fetch_list()

    # ② ID抽出
    ids = [extract_id(u) for u in list_urls]
    ids = [i for i in ids if i is not None]

    latest_list_id = max(ids) if ids else 0
    latest_seen_id = max([extract_id(u) for u in seen if extract_id(u)]) if seen else 0

    base = max(latest_list_id, latest_seen_id)

    print("base id:", base)

    # ③ 広めスキャン（取りこぼし防止）
    scan_range = range(base - 20, base + 50)

    candidates = []

    for i in scan_range:
        url = BASE_DETAIL + str(i)

        if url in seen:
            continue

        article = fetch_detail(url)

        if article:
            candidates.append(article)

    print("found:", len(candidates))

    # ④ 初回暴発防止
    if not seen and candidates:
        for a in candidates:
            seen.add(a["url"])
        save_seen(seen)
        print("initial skip")
        return

    # ⑤ 通知
    for a in sorted(candidates, key=lambda x: extract_id(x["url"])):
        send_discord(a)
        seen.add(a["url"])

    save_seen(seen)
    print("done")


if __name__ == "__main__":
    main()