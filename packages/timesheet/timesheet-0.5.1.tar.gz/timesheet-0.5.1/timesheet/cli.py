__author__ = 'vahid'

import argparse
import argcomplete
from timesheet.commands import get_available_commands


parser = argparse.ArgumentParser(description='Simple timesheet system, using python')
subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

for cmd in get_available_commands():
    cmd.create_parser(subparsers)

argcomplete.autocomplete(parser)


def parse_ars():
    # args, _reminder = parser.parse_known_args()
    args = parser.parse_args()
    return args
