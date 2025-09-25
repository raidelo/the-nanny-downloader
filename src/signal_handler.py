from console import console


def signal_handler(signal, frame):
    console.print("\nInterrupt received. Exitting ...")
    exit(1)
