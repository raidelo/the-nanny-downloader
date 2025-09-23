from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from requests.structures import CaseInsensitiveDict

from cli import parse_args
from constants import CHAPTER_MATCH
from functions import (
    download_archive,
    get_final_url,
    get_first_url,
    load_trid_mapping,
    get_path_for_chapter,
)


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
        print("error: Map of the url for each chapter wasn't found.")
        exit(1)

    for chapter in args.chapters:
        if not CHAPTER_MATCH.match(chapter):
            print("error: Chapter format doesn't match: %s" % chapter)
            exit(1)

    console = Console()
    console.print("\n[bold cyan]  The Nanny Downloader[/]")
    console.print(
        f"\n[bold green]Capítulos a descargar: [white]{', '.join(args.chapters)}[/]\n"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None),
        TextColumn("[green]{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        for chapter in args.chapters:
            first_url = get_first_url(chapter, args.delivery, trid_map, trdownload_map)
            final_url = get_final_url(first_url, args.delivery)

            if not final_url:
                console.print(
                    "[red bold]error:[/] Couldn't download chapter %s. It's url wasn't found."
                    % chapter
                )
                continue

            path_for_chapter = get_path_for_chapter(final_url, chapter)

            for pos, content_rcvd in enumerate(
                download_archive(final_url, path_for_chapter)
            ):
                if pos == 0 and isinstance(content_rcvd, tuple):
                    already_saved, to_save = content_rcvd
                    if not already_saved and not to_save:
                        console.print(
                            "[red bold]error:[/] Couldn't get enough information for chapter %s"
                            % chapter
                        )
                        break
                    console.print(f"[bold blue]  {path_for_chapter.name}  [/bold blue]")
                    task = progress.add_task(
                        "Descargando", total=already_saved + to_save
                    )
                    progress.update(task, advance=already_saved)
                    continue
                elif pos == 0 and not isinstance(content_rcvd, tuple):
                    console.print(
                        "[red bold]error:[/] Couldn't get headers for chapter %s"
                        % chapter
                    )
                    continue

                progress.update(task, advance=content_rcvd)

            progress.remove_task(task)
            console.print(
                "\n[bold green] Capítulo %s descargado con éxito[/]\n"
                % path_for_chapter.name
            )

        console.print("\n[bold green]✅ Descarga finalizada con éxito[/bold green]\n")

        # download_chapter(chapter, args.delivery, trid_map, trdownload_map)


if __name__ == "__main__":
    main()
