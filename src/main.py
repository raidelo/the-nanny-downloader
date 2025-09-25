from pathlib import Path
from urllib.parse import unquote_plus
from time import sleep

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from cli import parse_args
from constants import CHAPTER_MATCH
from functions import (
    download_archive,
    get_final_url,
    get_first_url,
    load_trid_mapping,
)


def start_getting_info_bar(progress: Progress, task):
    while True:
        progress.update(task)
        sleep(0.2)


def download_from_final_url(
    console: Console, progress: Progress, final_url: str, season: int
) -> int:
    filename = unquote_plus(Path(final_url.split("?")[0]).name)

    path = Path().joinpath("Season %d" % season).joinpath(filename)

    console.print(f"[bold blue]  {filename}  [/bold blue]")

    task = progress.add_task("Getting information ...", total=0)

    for pos, content_rcvd in enumerate(download_archive(final_url, path)):
        if pos == 0 and isinstance(content_rcvd, tuple):
            already_downloaded, to_download = content_rcvd
            if not already_downloaded and not to_download:
                return 1
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
        print("error: Mapping of each chapter's url wasn't found.")
        exit(1)

    chapters: list[tuple[int, int]] = []

    for chapter in args.chapters:
        m = CHAPTER_MATCH.match(chapter)
        if not m:
            print("error: Wrong chapter format: %s" % chapter)
            exit(1)
        chapters.append((int(m.group(1)), int(m.group(2))))

    console = Console()
    console.print("\n[bold cyan]  The Nanny Downloader[/]")
    console.print(
        f"\n[bold green]Capítulos a descargar: [white]{', '.join(args.chapters)}[/]"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None),
        TextColumn("[green]{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        for season, chapter in chapters:
            first_url = get_first_url(
                "%dx%d" % (season, chapter),
                args.delivery,
                trid_map,
                trdownload_map,
            )
            final_url = get_final_url(first_url, args.delivery)

            if not final_url:
                console.print(
                    "[red bold]error:[/] Can't download chapter %s. It's url wasn't found."
                    % chapter
                )
                continue

            return_code = download_from_final_url(
                console, progress, final_url, season, chapter
            )

            if return_code == 0:
                console.print(
                    "\n[bold green]✅ Descarga finalizada con éxito[/bold green]\n"
                )
                # console.print(
                #     "\n[bold green] Capítulo %s descargado con éxito[/]\n" % filename
                # )
            elif return_code == 1:
                console.print(
                    "[red bold]error:[/] Couldn't get enough information for chapter %dx%d"
                    % (season, chapter)
                )
            else:
                console.print(
                    "[red bold]error:[/] An unexpected error occurred when downloading: %dx%d"
                    % (season, chapter)
                )

        # download_chapter(chapter, args.delivery, trid_map, trdownload_map)


if __name__ == "__main__":
    main()
