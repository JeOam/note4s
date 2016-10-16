#!/usr/bin/env python

from tornado.options import define, options
from note4s.models import create_table

def parse_argument():
    define("command", help="The Command")
    options.parse_command_line()

def sync_db():
    create_table()

if __name__ == "__main__":
    parse_argument()

    def execute(args_list):
        args_list[0](*tuple(args_list[1:]))

    func_to_execute = {
        "sync_db": [sync_db],
    }
    execute(func_to_execute[options.command])