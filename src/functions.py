import json
from base64 import b64decode
from pathlib import Path
from urllib.parse import unquote_plus

from requests import get
from bs4 import BeautifulSoup

from constants import CHAPTER_MATCH, TRID_MAPPING_PATH, DEFAULT_USER_AGENT, TEMPLATE_URL
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


def get_path_for_chapter(url: str, chapter) -> Path:
    filename = unquote_plus(Path(url.split("?")[0]).name)

    m = CHAPTER_MATCH.match(chapter)

    if not m:
        raise InvalidChapter(chapter)

    return Path().joinpath("Season %s" % m.group(1)).joinpath(filename)


def download_archive(url, path: Path | None = None, resume: bool = True):
    """
    Descarga un archivo desde una URL con capacidad de reanudar la rescarga
    """

    # Si no se pasa nombre, lo toma del final de la URL
    if path is None:
        filename = Path(url.split("?")[0]).name or "archivo_descargado"
        path = Path().joinpath(filename)

    headers = {}
    written = 0
    open_mode = "wb"

    if resume and path.exists():
        written = path.stat().st_size
        if written != 0:
            open_mode = "ab"
            headers = {"Range": f"bytes={written}-"}

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, open_mode) as f:
        chunk = 4096  # tamaño del bloque de descarga

        with get(url, stream=True, headers=headers) as r:
            try:
                content_length = int(str(r.headers.get("Content-Length")))
            except ValueError:
                yield (0, 0)
                return

            if content_length == 0:
                yield (0, 0)
                return

            yield (written, content_length)

            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=chunk):
                if chunk:
                    yield f.write(chunk)
