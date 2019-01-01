#!/usr/bin/env python3
#
# fritz-dsl-mon - Monitor your DSL performance via your Fritz!Box 7430
# Copyright (C) 2019 Youri Ackx 
#  
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import ssl
import os
import sys
import traceback
from datetime import datetime
from fritzbox import FritzBox


def parse_args(sys_args):
    parser = argparse.ArgumentParser(description='Fritz!Box 7430 DSL monitoring')
    parser.add_argument('-u', '--user', default='admin', help='User name')
    parser.add_argument('-p', '--password', required=True, help='Password')
    parser.add_argument('-H', '--host', default='fritz.box', help='FritzBox URI')
    parser.add_argument('-d', '--dir', default='.', help='Storage directory')
    args = parser.parse_args(sys_args)
    
    host = args.host
    if not (host.startswith('http://') or host.startswith('https://')):
        host = 'http://' + host
    if host.endswith('/'):
        host = host[0:-1]
    
    if getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context
    
    fritz = FritzBox(args.user, args.password, host)

    return fritz, args.dir


def timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def process_stats(stats):
        today = datetime.today().strftime('%Y%m%d')
        file_path = os.path.join(directory, f'{today}{os.extsep}csv')
        mode = 'a' if os.path.exists(file_path) else 'w'
        with open(file_path, mode) as f:
            if mode is 'w':
                # Emit header
                f.write('timestamp,')
                f.write(",".join(stats.keys()))
                f.write("\n")
            f.write(timestamp())
            f.write(',')
            f.write(",".join(stats.values()))
            f.write("\n")


def process_exception(ex):
    ts = timestamp()
    tb_lines = [ line for line in
                 traceback.format_exception(ex.__class__, ex, ex.__traceback__)]
    tb_str = "\n".join(tb_lines)
    print(f'ERROR {tb_str}', file=sys.stderr)
    log_file = 'error.log'
    mode = 'a' if os.path.exists(log_file) else 'w'
    with open(log_file, mode) as f:
        f.write(f'{ts} {ex}:\n{tb_str}\n')


if __name__ == "__main__":
    try:
        fritz, directory = parse_args(sys.argv[1:])
        stats = fritz.load_dsl_stats()
        process_stats(stats)
    except Exception as ex:
        process_exception(ex)
    finally:
        fritz.logout()
