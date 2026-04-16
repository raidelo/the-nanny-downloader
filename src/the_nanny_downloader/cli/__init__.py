from argparse import ArgumentParser, Namespace, _SubParsersAction


def add_subcommand_download(subparser: _SubParsersAction) -> None:
    p_download = subparser.add_parser("download")

    p_download.add_argument("chapters", nargs="+")
    p_download.add_argument("-d", "--delivery", default="mediafire", dest="delivery")
    p_download.add_argument("-f", "--folder", dest="folder")


def add_subcommand_list(subparser: _SubParsersAction) -> None:
    subparser.add_parser("list")


def argument_parser() -> ArgumentParser:
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_subcommand_download(subparsers)
    add_subcommand_list(subparsers)

    return parser


def parse_args() -> Namespace:
    return argument_parser().parse_args()
