#!/usr/bin/env python

from tornado.options import define, options
from note4s.models import create_table, drop_table


def parse_argument():
    define("command", help="The Command")
    options.parse_command_line()


if __name__ == "__main__":
    parse_argument()


    def execute(args_list):
        args_list[0](*tuple(args_list[1:]))


    func_to_execute = {
        "create_table": [create_table],
        "drop_table": [drop_table],
    }
    execute(func_to_execute[options.command])
