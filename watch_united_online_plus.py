import requests
import re


URL = "https://jefunited.co.jp/my/uoplus/"


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}



r = requests.get(
    URL,
    headers=HEADERS,
    timeout=10
)


r.raise_for_status()



html = r.text



print(
    "html length:",
    len(html)
)



patterns = [

    r'https?://[^"\']+',

    r'["\']([^"\']*(?:api|ajax|json|uoplus)[^"\']*)["\']',

    r'fetch\((.*?)\)',

    r'\$\.ajax\((.*?)\)',

]



found = set()



for pattern in patterns:


    for m in re.findall(
        pattern,
        html,
        re.I
    ):


        if isinstance(m, tuple):

            m = m[0]


        found.add(m)





print(
    "=== FOUND ==="
)



for x in sorted(found):

    print(x)
