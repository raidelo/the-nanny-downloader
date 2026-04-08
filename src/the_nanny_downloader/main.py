from requests import RequestException
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from the_nanny_downloader.cli import argument_parser
from the_nanny_downloader.console import console
from the_nanny_downloader.constants import CHAPTER_MATCH, TRDOWNLOAD_MAPPING
from the_nanny_downloader.errors import InvalidChapter, InvalidDeliveryMethod
from the_nanny_downloader.utils import (
    download_from_final_url,
    get_final_url,
    get_first_url,
    load_trid_mapping,
    print_error,
)

type SeasonID = int
type ChapterID = int


def main():
    args = argument_parser().parse_args()

    try:
        trid_mapping = load_trid_mapping()
    except FileNotFoundError:
        print_error("TRID mapping file not found")
        return 1

    chapters: list[tuple[SeasonID, ChapterID]] = []

    for chapter in args.chapters:
        match = CHAPTER_MATCH.match(chapter)
        if match is None:
            print_error(f"Invalid chapter format: {chapter}")
            return 1
        chapters.append((int(match.group(1)), int(match.group(2))))

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
                    f"{season}x{chapter}",
                    args.delivery,
                    trid_mapping,
                    TRDOWNLOAD_MAPPING,
                )
            except InvalidChapter as e:
                print_error(f"Invalid chapter [bold]{e.chapter}")
                continue
            except InvalidDeliveryMethod as e:
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\nInterrupt received. Exitting ...")
