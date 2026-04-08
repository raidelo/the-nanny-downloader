from requests import Response, get

from the_nanny_downloader.constants import CHAPTER_MATCH, DEFAULT_HEADERS, TEMPLATE_URL
from the_nanny_downloader.errors import (
    ChapterNotFound,
    DeliveryMethodNotFound,
    InvalidChapterFormat,
)
from the_nanny_downloader.scrapping import get_final_url_from_mediafire
from the_nanny_downloader.types_ import ChapterInfo


def get_delivery_page(url: str, headers: dict[str, str] = DEFAULT_HEADERS) -> Response:
    return get(url, headers=headers)


def create_first_url(
    chapter: str,
    delivery_method: str,
    trid_mapping: dict[str, int],
    trdownload_map: dict[str, int],
) -> str:
    try:
        trdownload = trdownload_map[delivery_method]
    except KeyError:
        raise DeliveryMethodNotFound(delivery_method)
    try:
        trid = trid_mapping[chapter]
    except KeyError:
        raise ChapterNotFound(chapter)

    return TEMPLATE_URL % {"trdownload": trdownload, "trid": trid}


def get_final_url(first_url: str, delivery_method: str) -> str | None:
    delivery_resp = get_delivery_page(first_url)
    delivery_content = delivery_resp.content

    if delivery_method == "mediafire":
        return get_final_url_from_mediafire(delivery_content)
    else:
        raise NotImplementedError()


def chapter_parser(chapter: str) -> ChapterInfo:
    match = CHAPTER_MATCH.match(chapter)
    if match is None:
        raise InvalidChapterFormat(chapter)
    return (int(match.group(1)), int(match.group(2)))
