from base64 import b64decode

from bs4 import BeautifulSoup, Tag


def get_final_url_from_mediafire(page: bytes) -> str | None:
    soup = BeautifulSoup(page, "html.parser")
    a_tag = soup.find("a", {"id": "downloadButton"})

    if not isinstance(a_tag, Tag):
        return

    base64_encoded_url = a_tag.attrs.get("data-scrambled-url")

    if base64_encoded_url and isinstance(base64_encoded_url, str):
        return b64decode(base64_encoded_url).decode()
    else:
        url = a_tag.attrs.get("href")
        if url and isinstance(url, str):
            return url
        else:
            return
