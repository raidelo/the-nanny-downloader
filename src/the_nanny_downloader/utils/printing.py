from the_nanny_downloader.console import console


def print_error(string: str, default_msg_color: str = "white") -> None:
    console.print(f"[red bold]error:[/] [{default_msg_color}]{string}[/]\n")
