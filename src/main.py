from cli import parse_args
from constants import CHAPTER_MATCH
from functions import download_chapter, load_trid_mapping


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

    for chapter in args.chapters:
        download_chapter(chapter, args.delivery, trid_map, trdownload_map)


if __name__ == "__main__":
    main()
