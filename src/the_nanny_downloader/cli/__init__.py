from argparse import ArgumentParser, Namespace


def argument_parser() -> ArgumentParser:
    parser = ArgumentParser()

    parser.add_argument("chapters", nargs="+")
    parser.add_argument("-d", "--delivery", default="mediafire", dest="delivery")
    parser.add_argument("-f", "--folder", dest="folder")

    return parser


def parse_args() -> Namespace:
    return argument_parser().parse_args()
