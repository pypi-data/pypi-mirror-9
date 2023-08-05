# -*- coding: utf-8 -*-


import argparse
import os
import sys


def run_cli():
    base_dir = os.path.dirname(__file__) or '.'
    sys.path.insert(0, os.path.abspath(base_dir))
    sys.path.insert(0, os.path.join(os.path.abspath(os.pardir), "pyinfoepub"))

    from infoepub import PyInfoEpub
    from templates.cli import TemplateCLI

    parser = argparse.ArgumentParser(
        prog="PyInfoEpub", description='Extracts information from an epub file.')
    parser.add_argument('epub_file',
                        metavar='file.epub', type=argparse.FileType('r'),
                        default=sys.stdin, help='target epub file')
    parser.add_argument('--version', action='version', version='%(prog)s 0.2')

    args = parser.parse_args()

    pyob = PyInfoEpub(args.epub_file.name)
    extracted_info = pyob.get_info()

    tob = TemplateCLI(extracted_info)
    tob.render()


if __name__ == '__main__':
    run_cli()
else:
    # module imported
    pass
