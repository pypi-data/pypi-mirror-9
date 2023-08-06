#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#  Mongotail, Log all MongoDB queries in a "tail"able way.
#  Copyright (C) 2015 Mariano Ruiz (<https://github.com/mrsarm/mongotail>).
#
#  Author: Mariano Ruiz <mrsarm@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from __future__ import absolute_import
import sys, re, argparse
from .conn import connect
from .out import print_obj
from .err import error, error_parsing


__author__ = 'Mariano Ruiz'
__version__ = '0.1.0'
__license__ = 'GPL-3'
__url__ = 'https://github.com/mrsarm/mongotail'
__doc__ = """Mongotail, Log all MongoDB queries in a "tail"able way."""
__usage__ = """%(prog)s [db address] [options]

db address can be:
  foo                   foo database on local machine (IPv4 connection)
  192.169.0.5/foo       foo database on 192.168.0.5 machine
  192.169.0.5:9999/foo  foo database on 192.168.0.5 machine on port 9999
  "[::1]:9999/foo"      foo database on ::1 machine on port 9999 (IPv6 connection)"""

DEFAULT_LIMIT = 10
LOG_QUERY = {
        "ns": re.compile("^((?!\.system\.).)*$"),
        "command.profile": {"$exists": False},
        "command.collStats": {"$exists": False},
        "command.count": {"$ne": "system.profile"},
        "op": {"$ne":"getmore"},
}
LOG_FIELDS = ['ts', 'op', 'ns', 'query', 'updateobj', 'command', 'ninserted', 'ndeleted', 'nMatched']

def tail(client, db, lines, follow):
    cursor = db.system.profile.find(LOG_QUERY, fields=LOG_FIELDS)
    if lines.upper() != "ALL":
        try:
            skip = cursor.count() - int(lines)
        except ValueError:
            error_parsing('Invalid lines number "%s"' % lines)
        if skip > 0:
            cursor.skip(skip)
    if follow:
        cursor.add_option(2)  # Set the tailable flag
    while cursor.alive:
        try:
            result = next(cursor)
            print_obj(result)
        except StopIteration:
            pass


def set_profiling_level(client, db, level):
    try:
        db.set_profiling_level(int(level))
    except ValueError as e:
        err = str(e).replace("OFF", "0").replace("SLOW_ONLY", "1").replace("ALL", "2")
        error('Error configuring profiling level "%s". %s' % (level, err), -6)


def set_slowms_level(client, db, slowms):
    profiling_level = db.profiling_level()
    try:
        db.set_profiling_level(profiling_level, int(slowms))
    except (ValueError, TypeError) as e:
        error('Error configuring threshold in "%s". %s' % (slowms, str(e)), -7)


def main():
    try:
        # Parsing command line options
        parser = argparse.ArgumentParser(description=__doc__, usage=__usage__)
        egroup = parser.add_mutually_exclusive_group()
        parser.add_argument("-u", "--username", dest="username", default=None,
                            help="username for authentication")
        parser.add_argument("-p", "--password", dest="password", default=None,
                            help="password for authentication. If username is given and password isn't,\
                                  it's asked from tty.")
        parser.add_argument("-n", "--lines", dest="n", default=str(DEFAULT_LIMIT),
                            help="output the last N lines, instead of the last 10. Use ALL value to show all lines")
        parser.add_argument("-f", "--follow", dest="follow", action="store_true", default=False,
                            help="output appended data as the log grows")
        parser.add_argument("-l", "--level", dest="level", default=None,
                            help="Specifies the profiling level, which is either 0 for no profiling, "
                                 "1 for only slow operations, or 2 for all operations. "
                                 "USES this option once before logging the database")
        parser.add_argument("-s", "--slowms", dest="ms", default=None,
                            help="Sets the threshold in milliseconds for the profile to consider a query "
                                 "or operation to be slow (use with `--level 1`).")
        parser.add_argument('--version', action='version', version='%(prog)s ' + __version__ + "\n<" + __url__ + ">")
        args, address = parser.parse_known_args()
        if address and len(address) and address[0] == sys.argv[1]:
            address = address[0]
        elif len(address) == 0:
            error_parsing("db address expected")
        else:
            error_parsing()
        if address.startswith("-"):
            error_parsing()

        # Getting connection
        client, db = connect(address, args.username, args.password)

        # Execute command
        if args.level:
            set_profiling_level(client, db, args.level)
        elif args.ms:
            set_slowms_level(client, db, args.ms)
        else:
            tail(client, db, args.n, args.follow)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
