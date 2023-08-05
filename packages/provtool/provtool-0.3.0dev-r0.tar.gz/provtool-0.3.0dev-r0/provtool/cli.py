from __future__ import absolute_import, print_function

import argparse

from . import list, path, uuid, DEFAULT_PROVPROF_DIR


def cmd_list(args):
    dir = DEFAULT_PROVPROF_DIR
    print("%s:" % dir)
    for l in list(dir=dir):
        print(l)


def cmd_path(args):
    for p in path(args.name, patternMatch=args.pattern):
        print(p)


def cmd_uuid(args):
    print(uuid(args.path))


def main():
    parser = argparse.ArgumentParser(description='')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')

    parser_list = subparsers.add_parser('list', help='List installed Provisioning Profiles.')
    parser_list.set_defaults(func=cmd_list)

    parser_path = subparsers.add_parser('path', help='Get the path(s) of Provisioning Profile by name.')
    parser_path.add_argument('-p', '--pattern', action='store_true',
            required=False, default=False)
    parser_path.add_argument('name')
    parser_path.set_defaults(func=cmd_path)

    parser_uuid = subparsers.add_parser('uuid', help='Display the UDID of a Provisioning Profile by path.')
    parser_uuid.add_argument('path')
    parser_uuid.set_defaults(func=cmd_uuid)

    args = parser.parse_args()
    args.func(args)
