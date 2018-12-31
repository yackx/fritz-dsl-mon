#!/usr/bin/env python3
#
# fritzswitch - Switch your Fritz!DECT200 via command line
#
# Copyright (C) 2014 Richard "Shred" Körber
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
#

import argparse
import hashlib
import os
import ssl
import re
from urllib.request import urlopen
from xml.etree.ElementTree import parse

# Documentation of Fritz AHA see:
# http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AHA-HTTP-Interface.pdf


class FritzBox:
    def __init__(self, user, password, url):
        """Create a connection to the Fritz!Box with the given user and password"""
        self.fritzurl = url
        self.sid = self.get_sid(user, password)


    def get_sid(self, user, password):
        """Authenticate and get a Session ID"""
        with urlopen(self.fritzurl + '/login_sid.lua') as f:
            dom = parse(f)
            sid = dom.findtext('./SID')
            challenge = dom.findtext('./Challenge')
            print(f'original sid: {sid}, challenge: {challenge}')
        
        if sid == '0000000000000000':
            md5 = hashlib.md5()
            md5.update(challenge.encode('utf-16le'))
            md5.update('-'.encode('utf-16le'))
            md5.update(password.encode('utf-16le'))
            response = challenge + '-' + md5.hexdigest()
            uri = self.fritzurl + '/login_sid.lua?username=' + user + '&response=' + response
            with urlopen(uri) as f:
                dom = parse(f)
                sid = dom.findtext('./SID')

        if sid == '0000000000000000':
            raise PermissionError('access denied')

        print(f'sid: {sid}')
        return sid


    def logout(self):
        path = '/index.lua?sid=' + self.sid
        self.open_page(path)
        print('logged out')


    def load_dsl_stats(self):
        path = '/internet/dsl_stats_tab.lua?sid=' + self.sid
        with self.open_page(path) as f:
            result = f.read()
        print(result.decode())
        decoded = result.decode()

        max_dslam = self.scrape_values('Max. DSLAM throughput', decoded)
        attainable = self.scrape_values('Attainable throughput', decoded)
        current = self.scrape_values('Current throughput', decoded)
        seamless = self.scrape_values('Seamless rate adaptation', decoded)
        
        stats = {
                'max_dslam_throughput_down': max_dslam[1],
                'max_dslam_throughput_up': max_dslam[2],
                'attainable_throughput_down': attainable[1],
                'attainable_throughput_up': attainable[2],
                'current_throughput_down': current[1],
                'current_throughput_up': current[2],
                'seamless_rate_adaptation_down': seamless[1],
                'seamless_rate_adaptation_up': seamless[2],
        }
        print(f'*** stats {stats}')

        return stats
        

    def scrape_values(self, column_title, html_content):
        r = re.compile(r'<tr>'
            rf'<td class="c1">{column_title}</td>'
            r'<td class="c2">(.*)</td>'
            r'<td class="c3">(.*)</td>'
            r'<td class="c4">(.*)</td>'
            r'</tr>')
        return re.findall(r, html_content)[0]


    def open_page(self, path):
        uri = self.fritzurl + path
        return urlopen(uri)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FritzBox 7430 DSL speed check')
    parser.add_argument('-u', '--user', default='admin', help='User name')
    parser.add_argument('-p', '--password', required=True, help='Password')
    parser.add_argument('-H', '--host', default='fritz.box', help='FritzBox base URL')
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
        fritz.load_dsl_stats()
    finally:
        fritz.logout()
