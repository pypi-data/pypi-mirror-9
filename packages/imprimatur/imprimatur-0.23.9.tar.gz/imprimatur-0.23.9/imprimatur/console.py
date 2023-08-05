import imprimatur
import argparse
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        help="File containing the Imprimatur tests.",
        type=argparse.FileType())
    args = parser.parse_args()
    script_str = ''.join(args.file)

    for txt in imprimatur.run(script_str):
        if txt is None:
            exit(0)
        else:
            sys.stdout.write(txt)

    exit(1)
