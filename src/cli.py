from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("chapters", nargs="+")
    parser.add_argument(
        "-d", "--delivery", required=False, default="mediafire", dest="delivery"
    )

    return parser, parser.parse_args()
