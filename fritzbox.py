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
from dataclasses import dataclass

# Documentation of Fritz AHA see:
# http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AHA-HTTP-Interface.pdf


@dataclass
class DslStat:
    # Max DSLAM throughput (kbit/s)
    # Min is also available but not mapped
    max_dslam_throughput_down: int
    max_dslam_throughput_up: int

    # Attainable throughput (kbit/s)
    attainable_throughput_down: int
    attainable_throughput_up: int

    # Current throughput (kbit/s)
    current_throughput_down: int
    current_throughput_up: int

    # Seamless rate adaptation
    seamless_rate_adaptation_down: bool
    seamless_rate_adaptation_up: bool

    # Latency (a qualifier) (exact meaning and possible values unknown)
    latency_down: str
    latency_up: str

    # Impulse Noise Protection (INP) (unit not specified)
    impulse_noise_protection_down: int
    impulse_noise_protection_up: int

    # G.INP https://www.increasebroadbandspeed.co.uk/g.inp
    g_inp_down: bool
    g_inp_up: bool

    # Signal-to-noise ratio (dB)
    signal_to_noise_ratio_down: int
    signal_to_noise_ratio_up: int

    # Bitswap
    bitswap_down: bool
    bitswap_up: bool

    # Line attenuation (dB)
    line_attenuation_down: int
    line_attenuation_up: int
    
    # Approximate line length (m)
    approximate_line_length: int

    # Profile (eg 17a)
    profile: str

    # G.Vector (eg full)
    g_vector_down: str
    g_vector_up: str

    # Carrier record (eg A43)
    carrier_record_down: str
    carrier_record_up: str




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
        # print(result)
        decoded = result.decode()
        stats = dict()

        max_dslam = re.findall(self.build_html_regex('Max. DSLAM throughput'), decoded)[0]
        stats['max_dslam_throughput_down'] = max_dslam[0]
        stats['max_dslam_throughput_up'] = max_dslam[1]

        attainable = re.findall(self.build_html_regex('Attainable throughput'), decoded)[0]
        stats['attainable_throughput_down'] = attainable[0]
        stats['attainable_throughput_up'] = attainable[1]

        current = re.findall(self.build_html_regex('Current throughput'), decoded)[0]
        stats['current_throughput_down'] = current[0]
        stats['current_throughput_up'] = current[1]

        print(f'stats {stats}')
        
        dsl_stats = DslStat(
                max_dslam_throughput_down = max_dslam[0],
                max_dslam_throughput_up = max_dslam[1],
        )
        print(dsl_stats)

        return stats
        

    def build_html_regex(self, column_title):
        return re.compile(r'<tr>'
            rf'<td class="c1">{column_title}</td>'
            r'<td class="c2">kbit/s</td>'
            r'<td class="c3">(\d+)</td>'
            r'<td class="c4">(\d+)</td>'
            r'</tr>')


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
    fritz.load_dsl_stats()
    fritz.logout()
