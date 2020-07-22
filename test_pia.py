#!/usr/bin/env python3

import subprocess
import socket
from collections import defaultdict

def resolve(domain):
    return socket.gethostbyname_ex(domain)[2]

def test_reachability(ips):
    processes = [
        subprocess.Popen(
            ['ping', '-c', '1', '-W', '1', address],
            stdout=subprocess.PIPE, encoding='utf-8'
        ) for address in ips
    ]
    return [
        '1 packets transmitted, 1 received, 0% packet loss' in proc.communicate()[0]
        for proc in processes
    ]

def parse_ping_output(stdout):
    return '; '.join(stdout.strip().split('\n')[-2:])

def measure_ping(ips):
    reachable = test_reachability(ips)
    processes = [
        (subprocess.Popen(
            ['ping', '-c', '50', '-W', '1', address],
            stdout=subprocess.PIPE, encoding='utf-8'
        ) if ok else None) for ok, address in zip(reachable, ips)
    ]
    return [
        (parse_ping_output(proc.communicate()[0]) if proc is not None else None)
        for proc in processes
    ]


def main():
    regions = [
        'ae', 'albania', 'ar', 'au-melbourne', 'au-perth', 'au-sydney',
        'austria', 'ba', 'belgium', 'bg', 'ca-montreal', 'ca-ontario',
        'ca-toronto', 'ca-vancouver', 'czech', 'de-berlin', 'de-frankfurt',
        'denmark', 'ee', 'fi', 'france', 'gr', 'hungary', 'in', 'ireland',
        'is', 'israel', 'italy', 'jp', 'lt', 'lu', 'lv', 'md', 'mk', 'nl', 'no',
        'nz', 'poland', 'pt', 'ro', 'rs', 'sg', 'sk', 'spain', 'sweden',
        'swiss', 'tr', 'ua', 'uk-london', 'uk-manchester', 'uk-southampton',
        'us-atlanta', 'us-california', 'us-chicago', 'us-dal', 'us-denver',
        'us-east', 'us-florida', 'us-houston', 'us-lasvegas', 'us-nyc',
        'us-sea', 'us-siliconvalley', 'us-washingtondc', 'us-west', 'za',
    ]
    pia_domains = [region + '.privateinternetaccess.com' for region in regions]

    for i, domain in enumerate(pia_domains, 1):
        print(f'{i}/{len(pia_domains)}: {domain}')
        ips = resolve(domain)
        ips.sort(key=lambda ip: [int(v) for v in ip.split('.')])
        stats = measure_ping(ips)

        for ip, stat in zip(ips, stats):
            print(f'    {ip:<15} | {stat if stat is not None else "unreachable"}')

if __name__ == '__main__':
    main()
