#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2024-04-29
# File  : ssllabs_grade.py (wato check plugin)
#
# based on the ssllabs plugin from Karsten Schoeke karsten.schoeke@geobasis-bb.de
# see https://exchange.checkmk.com/p/ssllabs
#

# 2021-05-15: rewritten for CMK 2.0 by thl-cmk[at]outlook[dot]com
#             changed cache file name form host_address to ssl_host_address
# 2021-05-16: changed arguments to argparse
#             added options for publish results and max cache age
# 2024-05-01: refactoring
# 2024-05-16: fixed proxy usage
#             removed check_mk section -> no way to differentiate from checkmk agent section check_mk
# 2025-06-04: changed to expose API errors to the check plugin

# sample agent output (formatted)
# <<<check_mk>>>
# Version: 2.0.2
# AgentOS: linux
#
# <<<ssllabs_grade:sep(0)>>>
# [
#     {
#         "host": "thl-cmk.hopto.org",
#         "port": 443,
#         "protocol": "http",
#         "isPublic": false,
#         "status": "READY",
#         "startTime": 1714559152230,
#         "testTime": 1714559237958,
#         "engineVersion": "2.3.0",
#         "criteriaVersion": "2009q",
#         "endpoints": [
#             {"ipAddress": "91.4.75.201",
#              "serverName": "p5b044bc9.dip0.t-ipconnect.de",
#              "statusMessage": "Ready",
#              "grade": "A+",
#              "gradeTrustIgnored": "A+",
#              "hasWarnings": false,
#              "isExceptional": true,
#              "progress": 100,
#              "duration": 85530,
#              "delegation": 1
#              }
#         ]
#     },
#     {
#         "host": "checkmk.com",
#         "port": 443,
#         "protocol": "http",
#         "isPublic": false,
#         "status": "IN_PROGRESS",
#         "startTime": 1714563744895,
#         "engineVersion": "2.3.0",
#         "criteriaVersion": "2009q",
#         "endpoints": [
#             {
#                 "ipAddress": "2a0a:51c1:0:5:0:0:0:4",
#                 "serverName": "www.checkmk.com",
#                 "statusMessage": "Ready",
#                 "grade": "A+",
#                 "gradeTrustIgnored": "A+",
#                 "hasWarnings": false,
#                 "isExceptional": true,
#                 "progress": 100,
#                 "duration": 72254,
#                 "delegation": 1
#             },
#             {
#                 "ipAddress": "45.133.11.28",
#                 "serverName": "www.checkmk.com",
#                 "statusMessage": "In progress",
#                 "statusDetails": "TESTING_SESSION_RESUMPTION",
#                 "statusDetailsMessage": "Testing session resumption", "delegation": 1
#             }
#         ]
#     }
# ]
# <<<>>>

from argparse import Namespace
from collections.abc import Sequence
from json import dumps as json_dumps, loads as json_loads, JSONDecodeError
from pathlib import Path
from requests import get
from requests.exceptions import ConnectionError
from sys import stdout as sys_stdout
from time import time as now_time

from cmk.special_agents.utils.agent_common import special_agent_main
from cmk.special_agents.utils.argument_parsing import create_default_argument_parser
from cmk.utils.paths import tmp_dir

VERSION = '2.0.3'


class Args(Namespace):
    max_age: int
    proxy: str
    publish: str
    ssl_hosts: str
    timeout: float


def write_section(section: dict):
    sys_stdout.write('\n<<<ssllabs_grade:sep(0)>>>\n')
    sys_stdout.write(json_dumps(section))
    sys_stdout.write('\n<<<>>>\n')


def parse_arguments(argv: Sequence[str] | None) -> Args:
    """'Parse arguments needed to construct a URL and for connection conditions"""
    parser = create_default_argument_parser(__doc__)
    parser.description = 'This is a CKK special agent for the Qualys SSL Labs API to monitor SSL Certificate status'
    parser.add_argument(
        '--ssl-hosts', required=True, type=str,
        help='Comma separated list of FQDNs to test for',
    )
    parser.add_argument(
        '--proxy', required=False,
        help='URL to HTTPS Proxy i.e.: https://192.168.1.1:3128',
    )
    parser.add_argument(
        '--timeout', '-t', type=float, default=60,
        help='API call timeout in seconds',
    )
    parser.add_argument(
        '--publish', type=str, default='off', choices=['on', 'off'],
        help='Publish test results on ssllabs.com',
    )
    parser.add_argument(
        '--max-age', type=int, default=167,
        help='Maximum report age, in hours, if retrieving from "ssllabs.com" cache',
    )
    parser.epilog = (
        '\n\nAcnowlegement:\n'
        ' This agent is based on the work by Karsten Schoeke karsten[dot]schoeke[at]geobasis-bb[dot]de\n'
        ' see https://exchange.checkmk.com/p/ssllabs\n\n'
        f'written by thl-cmk[at]outlook[dot], Version: {VERSION}, '
        f'For more information see: https://thl-cmk.hopto.org\n'
    )
    return parser.parse_args(argv)


def connect_ssllabs_api(ssl_host_address: str, host_cache: str, args: Args, ) -> dict | None:
    #
    # https://github.com/ssllabs/ssllabs-scan
    #
    server = 'api.ssllabs.com'
    uri = 'api/v3/analyze'  # change to api v4 (?)
    max_age = args.max_age * 24  # default 1 day (1 week minus 1 hour)
    publish = args.publish  # default off
    from_cache = 'on'  # on | off
    # all_data = 'done'  # on | done
    ignore_mismatch = 'on'  # on | off
    start_new = 'on'

    # url for request webservice (&startNew={startNew}&all={all})
    url = (
        f'https://{server}/{uri}'
        f'?host={ssl_host_address}'
        f'&publish={publish}'
        f'&fromCache={from_cache}'
        f'&maxAge={max_age}'
        # f'&all={all_data}'
        f'&ignoreMismatch={ignore_mismatch}'
        # f'&startNew={start_new}'
    )
    proxies = {}
    if args.proxy is not None:
        proxies = {'https': args.proxy}
    try:
        response = get(
            url=url,
            timeout=args.timeout,
            proxies=proxies,
            headers={
                # 'User-Agent': f'CMK SSL Labs special agent {VERSION}',
            },
        )
    except ConnectionError as e:
        host_data = {'host': ssl_host_address, 'errors': ['status: ConnectionError', str(e)]}
    else:
        try:
            host_data = response.json()
        except JSONDecodeError as e:
            host_data = {'host': ssl_host_address, 'errors': ['status: JSONDecodeError', str(e)]}
        if host_data.get('status') == 'READY':
            Path(host_cache).write_text(response.text)
        elif host_data.get('errors'):
            host_data.update({'host': ssl_host_address})

    return host_data


def read_cache(host_cache: str) -> dict | None:
    try:
        data: dict = json_loads(Path(host_cache).read_text())
    except JSONDecodeError:
        return

    data.update({'from_agent_cache': True})
    return data


def agent_ssllsbs_main(args: Args) -> int:
    now = now_time()
    cache_dir = f'{tmp_dir}/agents/agent_ssllabs'
    cache_age = args.max_age + 86400
    ssl_hosts = args.ssl_hosts.split(',')

    # Output general information about the agent
    # sys_stdout.write('<<<check_mk>>>\n')
    # sys_stdout.write(f'Version: {VERSION}\n')
    # sys_stdout.write('AgentOS: linux\n')

    # create cache directory, if it not exists
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    data = []
    for ssl_host_address in ssl_hosts:
        host_cache = f'{cache_dir}/{ssl_host_address}'

        # check if cache file exists and is not older as cache_age
        if Path(host_cache).exists() and now - Path(host_cache).stat().st_mtime < cache_age:
            if host_data := read_cache(host_cache=host_cache):
                data.append(host_data)
        else:
            if host_data := connect_ssllabs_api(
                    ssl_host_address=ssl_host_address,
                    host_cache=host_cache,
                    args=args,
            ):
                data.append(host_data)

    if data:
        write_section(data)
    return 0


def main() -> int:
    return special_agent_main(parse_arguments, agent_ssllsbs_main)


if __name__ == '__main__':
    main()
