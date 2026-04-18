from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Generator
from urllib.parse import unquote_plus

from requests import RequestException, get, head
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from the_nanny_downloader.console import console
from the_nanny_downloader.constants import (
    DEFAULT_DOWNLOAD_FILENAME,
    TRDOWNLOAD_MAPPING,
)
from the_nanny_downloader.errors import (
    ChapterNotFound,
    DeliveryMethodNotFound,
)
from the_nanny_downloader.types_ import ChapterInfo
from the_nanny_downloader.utils import create_first_url, get_final_url, print_error


@dataclass
class DownloadStatus:
    downloaded: int
    total_size: int


def download_archive(
    url: str,
    path: Path | None = None,
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
        total_size = int(resp.headers.get("Content-Length") or 0) + local_size
        for data in resp.iter_content(chunk_size=chunk_size):
            if data:
                f.write(data)
                local_size += len(data)
                yield DownloadStatus(downloaded=local_size, total_size=total_size)


def download_from_final_url(
    console: Console,
    progress: Progress,
    final_url: str,
    folder_path: Path | None,
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


def download_chapters(
    chapters: list[ChapterInfo],
    trid_mapping: dict[str, int],
    args: Namespace,
) -> int:
    with Progress(
        TextColumn("[bold blue]Downloading"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        for season, chapter in chapters:
            try:
                first_url = create_first_url(
                    f"{season}x{chapter}",
                    args.delivery,
                    trid_mapping,
                    TRDOWNLOAD_MAPPING,
                )
            except ChapterNotFound as e:
                print_error(f"Invalid chapter [bold]{e.chapter}")
                continue
            except DeliveryMethodNotFound as e:
                print_error(f"Invalid delivery method [bold]{e.delivery_method}")
                continue

            final_url = get_final_url(first_url, args.delivery)

            if not final_url:
                print_error(
                    f"Can't download chapter [bold]{chapter}[/bold]. It's url wasn't found."
                )
                continue

            try:
                download_from_final_url(
                    console,
                    progress,
                    final_url,
                    args.folder,
                    season,
                )
            except RequestException:
                print_error(
                    f"An unexpected error occurred while downloading: [bold]{season}x{chapter}[/bold]"
                )
                return 1

            console.print(
                f"[bold green] Capítulo [bold]{season}x{chapter}[/bold] descargado con éxito[/]\n"
            )

        console.print("[bold green]✅ Descarga finalizada con éxito[/bold green]\n")

        return 0
