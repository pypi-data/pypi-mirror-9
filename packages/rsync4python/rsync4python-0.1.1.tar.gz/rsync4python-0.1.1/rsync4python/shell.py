import argparse
import logging

import rsync4python.rdiff


def signature(log, arguments):
    rsync4python.rdiff.rdiff_signature(arguments.base,
                                       arguments.signature)

def patch(log, arguments):
    rsync4python.rdiff.rdiff_patch(arguments.base,
                                   arguments.delta,
                                   arguments.final)


def main():
    argument_parser = argparse.ArgumentParser(
        prog='pyrdiff',
        description='Python-based rdiff utility')
    sub_arg_parser = argument_parser.add_subparsers(title='command')

    signature_parser = sub_arg_parser.add_parser('signature')
    signature_parser.add_argument('--base',
                                  required=True,
                                  type=str,
                                  help='Path to the input file')
    signature_parser.add_argument('--signature',
                                  required=True,
                                  type=str,
                                  help='Path to the output file')
    signature_parser.set_defaults(func=signature)

    patch_parser = sub_arg_parser.add_parser('patch')
    patch_parser.add_argument('--base',
                              required=True,
                              type=str,
                              help='Path to the input file')
    patch_parser.add_argument('--delta',
                              required=True,
                              type=str,
                              help='Path to the delta file')
    patch_parser.add_argument('--final',
                              required=True,
                              type=str,
                              help='Path to the output file')
    patch_parser.set_defaults(func=patch)

    arguments = argument_parser.parse_args()

    log = logging.getLogger()

    logfile = logging.FileHandler('.pyrdiff.log')
    logfile.setLevel(logging.DEBUG)
    log.addHandler(logfile)
    log.setLevel(logging.DEBUG)

    arguments.func(log, arguments)


if __name__ == "__main__":
    main()
