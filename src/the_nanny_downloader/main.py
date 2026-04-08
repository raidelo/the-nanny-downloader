from the_nanny_downloader.cli import parse_args
from the_nanny_downloader.console import console
from the_nanny_downloader.download import download_chapters
from the_nanny_downloader.errors import InvalidChapterFormat
from the_nanny_downloader.types_ import ChapterInfo
from the_nanny_downloader.utils import (
    chapter_parser,
    load_trid_mapping,
    print_error,
)


def _main() -> int:
    args = parse_args()

    try:
        trid_mapping = load_trid_mapping()
    except FileNotFoundError:
        print_error("TRID mapping file not found")
        return 1

    chapters: list[ChapterInfo] = []

    for chapter in args.chapters:
        try:
            value_pair = chapter_parser(chapter)
        except InvalidChapterFormat:
            print_error(f"Invalid chapter format: {chapter}")
            return 1
        chapters.append(value_pair)

    console.print("\n  [bold cyan]The Nanny Downloader[/]")
    console.print(
        f"\n[bold green]Capítulos a descargar: [white]{', '.join(args.chapters)}[/]\n"
    )

    download_chapters(chapters, trid_mapping, args)

    return 0


def main() -> int:
    try:
        return _main()
    except KeyboardInterrupt:
        console.print("\nInterrupt received. Exitting ...")
        return 0


if __name__ == "__main__":
    exit(main())
