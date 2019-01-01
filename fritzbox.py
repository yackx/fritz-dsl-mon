#!/usr/bin/env python3
#
# fritz-dsl-mon - Monitor your DSL performance via your Fritz!Box 7430
# Copyright (C) 2019 Youri Ackx 
#
# Contains fragments of 
# fritzswitch - Switch your Fritz!DECT200 via command line
# (sid with md5 encoded challenge)
# Copyright (C) 2014 Richard "Shred" Körber released under GNU GPL license
# https://github.com/shred/fritzswitch
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
import hashlib
import os
import ssl
import re
import collections
from urllib.request import urlopen
from xml.etree.ElementTree import parse

# Documentation of Fritz AHA (in German, similarities with Fritz!Box 7430):
# http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AHA-HTTP-Interface.pdf


class FritzBox:
    def __init__(self, user, password, url):
        """Create a connection to the Fritz!Box with the given user and password"""
        self.fritzurl = url
        self.sid = self.get_sid(user, password)


    def get_sid(self, user, password):
        """Authenticate and get a session ID"""
        with urlopen(self.fritzurl + '/login_sid.lua') as f:
            dom = parse(f)
            sid = dom.findtext('./SID')
            challenge = dom.findtext('./Challenge')
        
        empty_sid = '0' * 16
        encoding = 'utf-16le'
        if sid == empty_sid:
            md5 = hashlib.md5()
            md5.update(challenge.encode(encoding))
            md5.update('-'.encode(encoding))
            md5.update(password.encode(encoding))
            response = challenge + '-' + md5.hexdigest()
            uri = self.fritzurl + '/login_sid.lua?username=' + user + '&response=' + response
            with urlopen(uri) as f:
                dom = parse(f)
                sid = dom.findtext('./SID')

        if sid == empty_sid:
            raise PermissionError('access denied')

        return sid


    def logout(self):
        """Logout"""
        path = '/index.lua?sid=' + self.sid
        self.open_page(path)


    def load_dsl_stats(self):
        """Load DSL statistics by scraping HTML from DSL Information page"""
        path = '/internet/dsl_stats_tab.lua?sid=' + self.sid
        with self.open_page(path) as f:
            result = f.read()
        html = result.decode().strip().replace('\n', '')

        central_exchange_errors = self.scrape_values('Central exchange', html, 4)
        fritzbox_errors = self.scrape_values('FRITZ!Box', html, 4)

        max_dslam = self.scrape_values('Max. DSLAM throughput', html)
        attainable = self.scrape_values('Attainable throughput', html)
        current = self.scrape_values('Current throughput', html)
        seamless = self.scrape_values('Seamless rate adaptation', html)
        latency = self.scrape_values('Latency', html)
        inp = self.scrape_values('Impulse Noise Protection \\(INP\\)', html)
        g_inp = self.scrape_values('G.INP', html)
        snr_ratio = self.scrape_values('Signal-to-noise ratio', html)
        bitswap = self.scrape_values('Bitswap', html)
        line_attenuation = self.scrape_values('Line attenuation', html)
        approx_length = self.scrape_values('approximate line length', html)
        profile = self.scrape_values('Profile', html)
        g_vector = self.scrape_values('G.Vector', html)
        carrier_record = self.scrape_values('Carrier record', html)

        stats = collections.OrderedDict({
                # Max DSLAM throughput (kbit/s)
                # Min is also available but not mapped
                'max_dslam_throughput_down': max_dslam[1],
                'max_dslam_throughput_up': max_dslam[2],
                # Attainable throughput (kbit/s)
                'attainable_throughput_down': attainable[1],
                'attainable_throughput_up': attainable[2],
                # Current throughput (kbit/s)
                'current_throughput_down': current[1],
                'current_throughput_up': current[2],
                # Seamless rate adaptation
                'seamless_rate_adaptation_down': seamless[1],
                'seamless_rate_adaptation_up': seamless[2],
                 # Latency (a qualifier) (exact meaning and possible values unknown)
                'latency_down': latency[1],
                'latency_up': latency[2],
                # Impulse Noise Protection (INP) (unit not specified)
                'impulse_noise_protection_down': inp[1],
                'impulse_noise_protection_up': inp[2],
                # G.INP https://www.increasebroadbandspeed.co.uk/g.inp
                'g_inp_down': g_inp[1],
                'g_inp_up': g_inp[2],
                # Signal-to-noise ratio (dB)
                'signal_to_noise_ratio_down': snr_ratio[1],
                'signal_to_noise_ratio_up': snr_ratio[2],
                # Bitswap
                'bitswap_down': bitswap[1],
                'bitswap_up': bitswap[2],
                # Line attenuation (dB)
                'line_attenuation_down': line_attenuation[1],
                'line_attenuation_up': line_attenuation[2],
                # Approximate line length (m)
                'approximate_line_length': approx_length[1],
                # Profile (eg 17a)
                'profile': profile[0],
                # G.Vector (eg full)
                'g_vector_down': g_vector[1],
                'g_vector_up': g_vector[2],
                # Carrier record (eg A43)
                'carrier_record_down': carrier_record[1],
                'carrier_record_up': carrier_record[2],
                # FritzBox errors
                'fritzbox_seconds_with_errors': fritzbox_errors[0],
                'fritzbox_seconds_with_many_errors': fritzbox_errors[1],
                'fritzbox_crc_errors_per_minute': fritzbox_errors[2],
                'fritzbox_crc_errors_last_15_m': fritzbox_errors[3],
                # Central exchange errors
                'central_exchange_seconds_with_errors': central_exchange_errors[0],
                'central_exchange_seconds_with_many_errors': central_exchange_errors[1],
                'central_exchange_crc_errors_per_minute': central_exchange_errors[2],
                'central_exchange_crc_errors_last_15_m': central_exchange_errors[3],
        })
    
        return stats
        

    def scrape_values(self, column_title, html_content, how_nany = 3):
        """Scrape 3 or 4 column values from the DSL Information page"""
        assert how_nany in [3, 4]
        regex = (r'<tr>'
            rf'<td class="c1.*">{column_title}</td>'
            r'<td class="c2">(.*?)</td>'
            r'<td class="c3">(.*?)</td>'
            r'<td class="c4">(.*?)</td>')
        if how_nany is 4:
            regex += r'<td class="c5">(.*?)</td>'
        regex += r'</tr>'
        r = re.compile(regex)
        return re.findall(r, html_content)[0]


    def open_page(self, path):
        uri = self.fritzurl + path
        return urlopen(uri)


    def pretty_print(self, stats):
        for k, v in stats.items():
            print(f'{k}: {v}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fritz!Box 7430 DSL monitoring')
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
        stats = fritz.load_dsl_stats()
        fritz.pretty_print(stats)
    finally:
        fritz.logout()
