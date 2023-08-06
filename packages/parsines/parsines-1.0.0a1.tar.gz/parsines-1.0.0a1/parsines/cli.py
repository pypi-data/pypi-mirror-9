from argparse import ArgumentParser
import sys

from parsines.parser import INESFileParser
from parsines.reporters import json_report, plain_text_report


def get_args():
    parser = ArgumentParser(prog="ines-util", description="Print information about iNES formatted files.")
    parser.add_argument('inesfile', type=str, help="A path to an iNES ROM file.")
    parser.add_argument("--json", action="store_true", help="Print the information in a web friendly format.")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    parser = INESFileParser()
    try:
        with open(args.inesfile, "rb") as fob:
            ines_file = parser.parse(fob)
        if args.json:
            json_report(ines_file)
        else:
            plain_text_report(ines_file)
    except INESFileParser.InvalidHeaderConstant:
        sys.stderr.write("ERROR: Invalid Header Constant. This file is probably not a valid iNES ROM.\n")
        sys.exit(1)
