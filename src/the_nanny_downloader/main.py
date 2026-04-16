from argparse import Namespace

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

try:
    trid_mapping = load_trid_mapping()
except FileNotFoundError:
    print_error("TRID mapping file not found")
    exit(1)


def exec_download(args: Namespace) -> int:
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


def exec_list(_: Namespace) -> int:
    eq_than_last = True
    for chapter, identifier in trid_mapping.items():
        if not eq_than_last:
            print()
        print(f"  {chapter}: {identifier}")

    return 0


def _main() -> int:
    args = parse_args()

    if args.command == "download":
        return exec_download(args)

    elif args.command == "list":
        return exec_list(args)

    else:
        raise ValueError("unreachable")


def main() -> int:
    try:
        return _main()
    except KeyboardInterrupt:
        console.print("\nInterrupt received. Exitting ...")
        return 0


if __name__ == "__main__":
    exit(main())
