#!/usr/bin/env python3

import argparse
import ssl
import os
from datetime import datetime
from fritzbox import FritzBox

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fritz!Box 7430 DSL monitoring')
    parser.add_argument('-u', '--user', default='admin', help='User name')
    parser.add_argument('-p', '--password', required=True, help='Password')
    parser.add_argument('-H', '--host', default='fritz.box', help='FritzBox URI')
    parser.add_argument('-d', '--dir', default='.', help='Storage directory')
    args = parser.parse_args()
    
    host = args.host
    if not (host.startswith('http://') or host.startswith('https://')):
        host = 'http://' + host
    if host.endswith('/'):
        host = host[0:-1]
    
    if getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context
    
    fritz = FritzBox(args.user, args.password, host)
    try:
        stats = fritz.load_dsl_stats()
        today = datetime.today().strftime('%Y%m%d')
        file_path = os.path.join(args.dir, f'{today}{os.extsep}csv')
        mode = 'a' if os.path.exists(file_path) else 'w'
        with open(file_path, mode) as f:
            if mode is 'w':
                # Emit header
                f.write('timestamp,')
                f.write(",".join(stats.keys()))
                f.write("\n")
            f.write(datetime.now().strftime('%Y%m%d%H%M%S'))
            f.write(',')
            f.write(",".join(stats.values()))
            f.write("\n")
    finally:
        fritz.logout()
