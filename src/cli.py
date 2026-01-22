from argparse import ArgumentParser


def argument_parser() -> ArgumentParser:
    parser = ArgumentParser()

    parser.add_argument("chapters", nargs="+")
    parser.add_argument("-d", "--delivery", default="mediafire", dest="delivery")
    parser.add_argument("-f", "--folder", dest="folder")

    return parser
