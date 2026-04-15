import base64
from bs4 import BeautifulSoup

def decode(data):
    if not data:
        return ""
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="ignore")

def decode_html(data):
    html_data = decode(data)
    soup = BeautifulSoup(html_data, "html.parser")

    for tag in soup(["script", "style", "noscript", "img"]):
        tag.decompose()

    for tag in soup.find_all(attrs={"style": True}):
        if "display:none" in tag.get("style", ""):
            tag.decompose()

    for br in soup.find_all("br"):
        br.replace_with("\n")

    text = soup.get_text(separator="\n")

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    cleaned = []
    for line in lines:
        if "unsubscribe" in line.lower():
            continue
        if "let us know" in line.lower():
            continue
        cleaned.append(line)

    return "\n".join(cleaned)