import argparse
from software.signal_display.scintillator_display.compat.entrypoint import entrypoint

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--display", help="show the scintillator display",
                        action="store_true")
    args = parser.parse_args()
    if args.display:
        entrypoint()