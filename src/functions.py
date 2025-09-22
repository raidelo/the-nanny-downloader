import json
from base64 import b64decode
from subprocess import Popen

from requests import get
from bs4 import BeautifulSoup

from constants import TRID_MAPPING_PATH, DEFAULT_USER_AGENT
from errors import InvalidDeliveryMethod, InvalidChapter


def load_trid_mapping() -> dict | None:
    with open(TRID_MAPPING_PATH, "rb") as jsonfile:
        return json.load(jsonfile)


def get_delivery_page(url: str, user_agent: str = DEFAULT_USER_AGENT):
    return get(url, headers={"User-Agent": user_agent})


def get_final_url_from_mediafire(page: bytes) -> str | None:
    a_tag = BeautifulSoup(page, "html.parser").find("a", {"id": "downloadButton"})

    if not a_tag:
        return

    scrambled_url = str(a_tag.attrs.get("data-scrambled-url"))

    if not scrambled_url:
        return

    return b64decode(scrambled_url.encode()).decode()


def get_first_url(
    chapter: str, delivery_method: str, trid_map: dict, trdownload_map: dict
) -> str:
    try:
        trdownload = trdownload_map[delivery_method]
    except KeyError:
        raise InvalidDeliveryMethod(delivery_method)
    try:
        trid = trid_map[chapter]
    except KeyError:
        raise InvalidChapter(chapter)

    return TEMPLATE_URL % {"trdownload": trdownload, "trid": trid}


def get_final_url(first_url: str, delivery_method: str) -> str | None:
    delivery_resp = get_delivery_page(first_url)
    delivery_content = delivery_resp.content

    if delivery_method == "mediafire":
        return get_final_url_from_mediafire(delivery_content)
    else:
        raise NotImplementedError


def download_from_final_url(url: str):
    s = Popen(["wget.exe", url])

    return s.wait()


def download_chapter(
    chapter: str, delivery_method: str, trid_map: dict, trdownload_map: dict
):
    first_url = get_first_url(chapter, delivery_method, trid_map, trdownload_map)
    final_url = get_final_url(chapter, delivery_method)

    if final_url:
        print("Downloading chapter <%s> from <%s>" % (chapter, delivery_method))
        print("DEBUG: first url: %s" % first_url)
        print("DEBUG: final url: %s" % final_url)

        download_from_final_url(final_url)
    else:
        print("error: Couldn't download chapter %s. It's url wasn't found." % chapter)
