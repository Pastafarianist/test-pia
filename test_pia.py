#!/usr/bin/env python3

import socket
import subprocess

import joblib


def resolve(domain):
    ips = socket.gethostbyname_ex(domain)[2]
    ips.sort(key=lambda ip: [int(v) for v in ip.split('.')])
    return ips


def parse_ping_output(stdout):
    return '; '.join(stdout.strip().split('\n')[-2:])


def measure_ping(ip):
    proc = subprocess.Popen(
        ['ping', '-c', '1', '-W', '1', ip],
        stdout=subprocess.PIPE, encoding='utf-8'
    )
    reachable = '1 packets transmitted, 1 received, 0% packet loss' in proc.communicate()[0]
    if reachable:
        proc = subprocess.Popen(
            ['ping', '-c', '50', '-W', '1', ip],
            stdout=subprocess.PIPE, encoding='utf-8'
        )
        return parse_ping_output(proc.communicate()[0])
    else:
        return None


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

    domain2ips = {}
    all_ips = []

    print('Resolving domain names to IPs...')
    domain2ips = dict(zip(pia_domains, joblib.Parallel(n_jobs=min(len(pia_domains), 128), verbose=10)(
        joblib.delayed(resolve)(domain) for domain in pia_domains
    )))
    print(f'Done, total: {len(all_ips)} IPs.')

    all_ips = [ip for ips in domain2ips.values() for ip in ips]

    print('Pinging all IPs in 1024 threads...')
    ip2stats = dict(zip(all_ips, joblib.Parallel(n_jobs=min(len(all_ips), 1024), prefer='threads', verbose=10)(
        joblib.delayed(measure_ping)(ip) for ip in all_ips
    )))

    for i, (domain, ips) in enumerate(domain2ips.items(), 1):
        print(f'{i}/{len(pia_domains)}: {domain}')

        for ip in ips:
            stat = ip2stats[ip]
            print(f'    {ip:<15} | {stat if stat is not None else "unreachable"}')


if __name__ == '__main__':
    main()
