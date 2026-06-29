import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://jefunited.co.jp"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# -------------------------
# HTTP
# -------------------------

def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.text


# -------------------------
# 方法1: HTML直抽出
# -------------------------

def extract_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    results = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/my/uoplus/detail/" not in href:
            continue

        url = urljoin(base_url, href).split("?")[0]

        if url in seen:
            continue
        seen.add(url)

        title = a.get_text(" ", strip=True)
        if not title:
            title = "UNITED ONLINE PLUS"

        results.append({
            "url": url,
            "title": title
        })

    return results


# -------------------------
# 方法2: JSON埋め込み探索
# -------------------------

def extract_from_json(html):
    # script内のJSONっぽい塊を拾う
    match = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

    for m in match:
        if "uoplus" in m or "article" in m:
            try:
                data = json.loads(m)
                return data
            except:
                continue

    return None


# -------------------------
# メイン抽出
# -------------------------

def fetch_articles():
    url = "https://jefunited.co.jp/my/uoplus/list?c=article"

    html = get_html(url)

    # ① HTMLから
    articles = extract_from_html(html, BASE)

    if articles:
        return articles

    # ② JSON探索（失敗したら次へ）
    json_data = extract_from_json(html)
    if json_data:
        print("[INFO] JSON found but parser not mapped")

    # ③ 最終手段（JSページ対策）
    print("[WARN] falling back needed (likely JS rendered page)")

    return []


# -------------------------
# テスト
# -------------------------

if __name__ == "__main__":
    articles = fetch_articles()

    print("ARTICLES:", len(articles))
    for a in articles[:10]:
        print(a)
