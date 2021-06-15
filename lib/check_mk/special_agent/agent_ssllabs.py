#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Karsten Schoeke <karsten.schoeke@geobasis-bb.de>
#
# 2021-05-15: rewritten for CMK 2.0 by thl-cmk[at]outlook[dot]com
#             changed cache file name form host_address to ssl_host_address
# 2021-05-16: changed arguments to argparse
#             added options for publish results and max cache age
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

import argparse
import json
import os
import requests
import sys
import time
from typing import Optional, Sequence

from cmk.utils.paths import tmp_dir


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    ''''Parse arguments needed to construct an URL and for connection conditions'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--sslhosts', required=True, type=str, help='Comma separated list of FQDNs to test for')
    parser.add_argument('--proxy', required=False, help='URL to HTTPS Proxy i.e.: https://192.168.1.1:3128')
    parser.add_argument('--timeout', '-t', type=float, default=60, help='API call timeout in seconds', )
    parser.add_argument('--publish', type=str, default='off', help='Publish test results on ssllabs.com', choices=['on', 'off'] )
    parser.add_argument('--maxage', type=int, default=167, help='Maximum report age, in hours, if retrieving from "ssllabs.com" cache', )

    return parser.parse_args(argv)


def connect_ssllabs_api(ssl_host_address: str, host_cache: str, args: argparse.Namespace, ):
    server = 'api.ssllabs.com'
    uri = 'api/v3/analyze'
    maxAge = args.maxage  # default 167 (1 week minus 1 hour)
    publish = args.publish  # default off
    fromCache = 'on'
    now = time.time()

    # url for request webservice (&startNew={startNew}&all={all})
    url = f'https://{server}/{uri}?host={ssl_host_address}&publish={publish}&fromCache={fromCache}&maxAge={maxAge}'
    proxies = {}
    if args.proxy is not None:
        proxies = {'https': args.proxy.split('/')[-1]}  # remove 'https://' from proxy string

    try:
        response = requests.get(
            url=url,
            timeout=args.timeout,
            proxies=proxies,
        )

        jsonData = json.loads(response.text)

    except Exception as err:
        sys.stdout.write(f'{ssl_host_address} Connection error: {err} on {url}')
        # print(f'{ssl_host_address};{err};{now};2')
        return

    print(response.text)

    try:
        if jsonData['status'] == 'READY':
            # if test finish and json data ok --> write data in cache file
            with open(host_cache, 'w') as outfile:
                json.dump(jsonData, outfile)

    except (ValueError, KeyError, TypeError):
        print(f'{ssl_host_address};request JSON format error;{now};2')   # ;{grade_cache}


def read_cache(host_cache: str):
    # read cache file
    with open(host_cache) as json_file:
        # check if cache file contains valid json data
        try:
            jsonData = json.load(json_file)
            if jsonData['status'] == 'READY':
                print(json.dumps(jsonData))
        except (ValueError, KeyError, TypeError):
            # print(f'{ssl_host_address};cache JSON format error;{now};2;{grade_cache}')
            return


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_arguments(argv)

    VERSION = '2.0.1'
    now = time.time()
    cache_dir = tmp_dir + '/agents/agent_ssllabs'
    cache_age = args.maxage
    ssl_hosts = args.sslhosts.split(',')

    # Output general information about the agent
    sys.stdout.write('<<<check_mk>>>\n')
    sys.stdout.write('Version: %s\n' % VERSION)
    sys.stdout.write('AgentOS: linux\n')

    # create cache directory, if not exists
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    print('<<<ssllabs_grade:sep(0)>>>')

    for ssl_host_address in ssl_hosts:
        # changed cache file form host_address to ssl_host_address
        host_cache = '%s/%s' % (cache_dir, ssl_host_address)

        # check if cache file exists and is not older as cache_age
        if not os.path.exists(host_cache):
            connect_ssllabs_api(
                ssl_host_address=ssl_host_address,
                host_cache=host_cache,
                args=args)
        else:
            json_cache_file_age = os.path.getmtime(host_cache)
            cache_age_sec = now - json_cache_file_age
            if cache_age_sec < cache_age:
                read_cache(
                    host_cache=host_cache,
                            )
            else:
                connect_ssllabs_api(
                    ssl_host_address=ssl_host_address,
                    host_cache=host_cache,
                    args=args
                )


if __name__ == '__main__':
    main()
