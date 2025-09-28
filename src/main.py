from pathlib import Path
from signal import signal, SIGINT, SIGTERM
from urllib.parse import unquote_plus

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from cli import parse_args
from constants import CHAPTER_MATCH
from console import console
from errors import InvalidChapter, InvalidDeliveryMethod
from functions import (
    download_archive,
    get_final_url,
    get_first_url,
    load_trid_mapping,
)
from signal_handler import signal_handler

signal(SIGINT, signal_handler)
signal(SIGTERM, signal_handler)

SeasonID = int
ChapterID = int


def download_from_final_url(
    console: Console,
    progress: Progress,
    final_url: str,
    folder: str | None,
    season: int,
) -> int:
    filename = unquote_plus(Path(final_url.split("?")[0]).name)

    path = (
        Path(folder).resolve() if folder else Path().joinpath("Season %d" % season)
    ).joinpath(filename)

    console.print(f"[bold blue]  {filename}  [/bold blue]")

    task = progress.add_task(
        "Getting information ...", start=False, total=0, filename=filename
    )

    for pos, content_rcvd in enumerate(download_archive(final_url, path)):
        if pos == 0 and isinstance(content_rcvd, tuple):
            already_downloaded, to_download = content_rcvd
            if not already_downloaded and not to_download:
                return 1
            progress.start_task(task)
            progress.update(
                task,
                description="Downloading",
                total=already_downloaded + to_download,
                completed=already_downloaded,
            )
            continue
        elif pos == 0 and not isinstance(content_rcvd, tuple):
            return 1
        elif pos != 0 and isinstance(content_rcvd, int):
            progress.update(task, advance=content_rcvd)
        else:
            return 2

    progress.remove_task(task)

    return 0


def main():
    _parser, args = parse_args()

    trdownload_map = {
        # None: 0, # TODO
        # None: 1, # TODO
        # None: 2, # TODO
        "mediafire": 3,
        "mega": 4,
    }

    trid_map = load_trid_mapping()
    if not trid_map:
        print("error: Mapping file of each chapter's url wasn't found.")
        exit(1)

    chapters: list[tuple[SeasonID, ChapterID]] = []

    for chapter in args.chapters:
        m = CHAPTER_MATCH.match(chapter)
        if not m:
            print("error: Wrong chapter format: %s" % chapter)
            exit(1)
        chapters.append((int(m.group(1)), int(m.group(2))))

    console.print("\n  [bold cyan]The Nanny Downloader[/]")
    console.print(
        f"\n[bold green]Capítulos a descargar: [white]{', '.join(args.chapters)}[/]\n"
    )

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
                first_url = get_first_url(
                    "%dx%d" % (season, chapter),
                    args.delivery,
                    trid_map,
                    trdownload_map,
                )
            except InvalidChapter as e:
                console.print(
                    "[red bold]error:[/] [white]Invalid chapter [bold]%s[/white]\n"
                    % e.chapter
                )
                continue
            except InvalidDeliveryMethod as e:
                console.print(
                    "[red bold]error:[/] [white]Invalid delivery method [bold]%s[/white]\n"
                    % e.delivery_method
                )
                continue

            final_url = get_final_url(first_url, args.delivery)

            if not final_url:
                console.print(
                    "[red bold]error:[/] [white]Can't download chapter [bold]%s[/bold]. It's url wasn't found.[/white]\n"
                    % chapter
                )
                continue

            return_code = download_from_final_url(
                console, progress, final_url, args.folder, season
            )

            if return_code == 0:
                console.print(
                    "[bold green]✅ Descarga finalizada con éxito[/bold green]\n"
                )
                # console.print(
                #     "[bold green] Capítulo %s descargado con éxito[/]\n" % filename
                # )
            elif return_code == 1:
                console.print(
                    "[red bold]error:[/] [white]Couldn't get enough information for chapter [bold]%dx%d[/]\n"
                    % (season, chapter)
                )
            else:
                console.print(
                    "[red bold]error:[/] [white]An unexpected error occurred when downloading: [bold]%dx%d[/]\n"
                    % (season, chapter)
                )


if __name__ == "__main__":
    main()
