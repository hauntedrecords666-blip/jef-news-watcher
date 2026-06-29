from playwright.sync_api import sync_playwright
import json

URL = "https://jefunited.co.jp/my/uoplus/"


def find_api_calls():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def on_request(req):
            # XHR / fetchだけ拾う
            if req.resource_type in ["xhr", "fetch"]:
                if "jefunited.co.jp" in req.url:
                    results.append(req.url)

        page.on("request", on_request)

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(5000)

        browser.close()

    # 重複排除
    return sorted(set(results))


def main():
    print("=== API DISCOVERY START ===")

    apis = find_api_calls()

    print("[FOUND ENDPOINTS]")
    for a in apis:
        print(a)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
