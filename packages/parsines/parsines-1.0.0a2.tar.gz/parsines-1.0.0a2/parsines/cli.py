from argparse import ArgumentParser
import sys
from os import walk
from os.path import split, isdir, join

from parsines.parser import INESFileParser
from parsines.reporters import json_report, plain_text_report, json_report_directory


def get_args():
    parser = ArgumentParser(prog="ines-util",
                            description="Print information about iNES formatted files.",
                            epilog="Pass a directory name with the JSON flag in order to output a JSON array for all files.")
    parser.add_argument('inesfile', type=str, help="A path to an iNES ROM file.")
    parser.add_argument("--json", action="store_true", help="Print the information in a web friendly format.")
    args = parser.parse_args()
    return args


def process_directory(args):
    dirpath, dirnames, filenames = next(walk(args.inesfile))
    parser = INESFileParser()
    ines_files = list()
    for filename in filenames:
        if filename.endswith(".nes"):
            path = join(dirpath, filename)
            with open(path, "rb") as fob:
                try:
                    ines_file = parser.parse(fob, filename=filename)
                    ines_files.append(ines_file)
                except INESFileParser.InvalidHeaderConstant:
                    print("ERROR: Bad header constant, skipping %s" % path)
    json_report_directory(ines_files)


def process_single_file(args):
    parser = INESFileParser()    
    with open(args.inesfile, "rb") as fob:
        ines_file = parser.parse(fob, filename=split(args.inesfile)[-1])
    if args.json:
        json_report(ines_file)
    else:
        plain_text_report(ines_file)

def main():
    args = get_args()
    try:
        if isdir(args.inesfile) and args.json:
            process_directory(args)
        elif isdir(args.inesfile):
            sys.stderr.write("ERROR: directories only supported for the --json argument."
                             " There are better ways of running ines-util on a directory for plain text. (see 'find -exec')\n")
        else:
            process_single_file(args)
    except INESFileParser.InvalidHeaderConstant:
        sys.stderr.write("ERROR: Invalid Header Constant. This file is probably not a valid iNES ROM.\n")
        sys.exit(1)
