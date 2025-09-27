from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("chapters", nargs="+")
    parser.add_argument(
        "-d", "--delivery", required=False, default="mediafire", dest="delivery"
    )
    parser.add_argument("-p", "--folder", dest="folder")

    return parser, parser.parse_args()
