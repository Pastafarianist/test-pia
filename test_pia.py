#!/usr/bin/env python3

import socket
import subprocess

import joblib
import tqdm


def resolve(domain):
    return socket.gethostbyname_ex(domain)[2]


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
    for domain in tqdm.tqdm(pia_domains):
        ips = resolve(domain)
        ips.sort(key=lambda ip: [int(v) for v in ip.split('.')])
        domain2ips[domain] = ips
        all_ips.extend(ips)
    print(f'Done, total: {len(all_ips)} IPs.')

    print('Pinging all IPs in 64 threads...')
    ip2stats = dict(zip(all_ips, joblib.Parallel(n_jobs=64, prefer='threads', verbose=10)(
        joblib.delayed(measure_ping)(ip) for ip in all_ips
    )))

    for i, (domain, ips) in enumerate(domain2ips.items(), 1):
        print(f'{i}/{len(pia_domains)}: {domain}')

        for ip in ips:
            stat = ip2stats[ip]
            print(f'    {ip:<15} | {stat if stat is not None else "unreachable"}')


if __name__ == '__main__':
    main()
