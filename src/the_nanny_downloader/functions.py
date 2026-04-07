import json
from base64 import b64decode
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Mapping, Optional
from urllib.parse import unquote_plus

from bs4 import BeautifulSoup, Tag
from requests import Response, get, head
from rich.console import Console
from rich.progress import Progress

from console import console
from constants import (
    DEFAULT_DOWNLOAD_FILENAME,
    DEFAULT_USER_AGENT,
    TEMPLATE_URL,
    TRID_MAPPING_PATH,
)
from errors import InvalidChapter, InvalidDeliveryMethod


def load_trid_mapping() -> Mapping[str, str]:
    with open(TRID_MAPPING_PATH, "rb") as jsonfile:
        return json.load(jsonfile)


def get_delivery_page(url: str, user_agent: str = DEFAULT_USER_AGENT) -> Response:
    return get(url, headers={"User-Agent": user_agent})


def get_final_url_from_mediafire(page: bytes) -> Optional[str]:
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


def get_first_url(
    chapter: str,
    delivery_method: str,
    trid_mapping: Mapping[str, str],
    trdownload_map: Mapping[str, int],
) -> str:
    try:
        trdownload = trdownload_map[delivery_method]
    except KeyError:
        raise InvalidDeliveryMethod(delivery_method)
    try:
        trid = trid_mapping[chapter]
    except KeyError:
        raise InvalidChapter(chapter)

    return TEMPLATE_URL % {"trdownload": trdownload, "trid": trid}


def get_final_url(first_url: str, delivery_method: str) -> Optional[str]:
    delivery_resp = get_delivery_page(first_url)
    delivery_content = delivery_resp.content

    if delivery_method == "mediafire":
        return get_final_url_from_mediafire(delivery_content)
    else:
        raise NotImplementedError()


@dataclass
class DownloadStatus:
    downloaded: int
    total_size: int


def download_archive(
    url: str,
    path: Optional[Path] = None,
    resume: bool = True,
) -> Generator[DownloadStatus, None, None]:
    """
    Downloads a file from the given URL, optionally resuming a partial download.

    Args:
        url: URL of the file to download.
        path: Local path where the file will be saved. If None, the filename
            is derived from the URL or defaults to a predefined name.
        resume: Whether to attempt resuming an incomplete download if the
            local file exists and the server supports HTTP Range.

    Yields:
        The total number of bytes written after each chunk is downloaded.

    Notes:
        - If the file already exists and the server provides `Content-Length`,
          the function checks whether the download is complete and returns immediately.
        - If the server supports HTTP Range, the function resumes incomplete downloads.
        - Data is written in chunks of 4096 bytes.
        - Servers that do not provide `Content-Length` or do not support Range
          will result in a full download from scratch.
    """
    if path is None:
        filename = Path(url.split("?")[0]).name or DEFAULT_DOWNLOAD_FILENAME
        path = Path(filename)

    headers = {}
    local_size = 0
    open_mode = "wb"

    if path.exists() and resume:
        local_size = path.stat().st_size
        total_size = head(url=url).headers.get("Content-Length")
        if total_size is not None:
            total_size = int(total_size)
            s = DownloadStatus(downloaded=local_size, total_size=total_size)
            if local_size >= total_size:
                yield s  # complete download
                return

            headers["Range"] = f"bytes={local_size}-"
            open_mode = "ab"
            yield s  # partial download

    chunk_size = 4096

    path.resolve().parent.mkdir(parents=True, exist_ok=True)

    with (
        open(path, open_mode) as f,
        get(url=url, stream=True, headers=headers) as resp,
    ):
        resp.raise_for_status()
        total_size = int(resp.headers.get("Content-Length") or 0)
        for data in resp.iter_content(chunk_size=chunk_size):
            if data:
                f.write(data)
                local_size += len(data)
                yield DownloadStatus(downloaded=local_size, total_size=total_size)


def download_from_final_url(
    console: Console,
    progress: Progress,
    final_url: str,
    folder_path: Optional[Path],
    season: int,
) -> None:
    filename = unquote_plus(Path(final_url.split("?")[0]).name)

    path = (
        (folder_path or Path().joinpath(f"Season {season}"))
        .resolve()
        .joinpath(filename)
    )

    console.print(f"[bold blue]  {filename}  [/bold blue]")

    task = progress.add_task(
        "Getting information ...",
        start=False,
        total=0,
        filename=filename,
    )

    progress.start_task(task)

    for content_rcvd in download_archive(final_url, path):
        progress.update(
            task,
            description="Downloading",
            total=content_rcvd.total_size,
            completed=content_rcvd.downloaded,
        )

        progress.update(task, completed=content_rcvd.downloaded)

    progress.remove_task(task)


def print_error(string: str, default_msg_color: str = "white") -> None:
    console.print(f"[red bold]error:[/] [{default_msg_color}]{string}[/]\n")
