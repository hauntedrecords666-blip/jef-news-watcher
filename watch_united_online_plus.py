import requests


URL = "https://jefunited.co.jp/my/uoplus/"

r = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=10
)

print("status", r.status_code)

with open(
    "uoplus_debug.html",
    "w",
    encoding="utf-8"
) as f:

    f.write(r.text)


print(
    "detail count:",
    r.text.count("/my/uoplus/detail/")
)

print(
    "column count:",
    r.text.count("column")
)

print(
    "report count:",
    r.text.count("report")
)

print(
    "video count:",
    r.text.count("video")
)
