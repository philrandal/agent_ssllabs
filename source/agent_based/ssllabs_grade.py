#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2024-04-29
# File  : ssllabs_grade.py (check plugin)

# based on the ssllabs plugin from Karsten Schoeke karsten.schoeke@geobasis-bb.de
# see https://exchange.checkmk.com/p/ssllabs

# 2024-05-06: added pending to ok states for end points
# 2024-05-07: fixed crash on wrong params int "ERROR" state
#             changed max CMK version in package info to 2.3.0b1
# 2024-06-04: added support for API error messages

# sample string_table:
# [
#     {
#         "host": "thl-cmk.hopto.org",
#         "port": 443,
#         "protocol": "http",
#         "isPublic": False,
#         "status": "READY",
#         "startTime": 1714559152230,
#         "testTime": 1714559237958,
#         "engineVersion": "2.3.0",
#         "criteriaVersion": "2009q",
#         "endpoints": [
#             {
#                 "ipAddress": "91.4.75.201",
#                 "serverName": "p5b044bc9.dip0.t-ipconnect.de",
#                 "statusMessage": "Ready",
#                 "grade": "A+",
#                 "gradeTrustIgnored": "A+",
#                 "hasWarnings": False,
#                 "isExceptional": True,
#                 "progress": 100,
#                 "duration": 85530,
#                 "delegation": 1
#             }
#         ]
#     },
#     {
#         "host": "checkmk.com",
#         "port": 443,
#         "protocol": "http",
#         "isPublic": False,
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
#                 "hasWarnings": False,
#                 "isExceptional": True,
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
#


from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from json import loads as json_loads, JSONDecodeError
from typing import Tuple
from re import compile as re_compile, match as re_match
from time import time as now_time

from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Result,
    Service,
    State,
    check_levels,
    register,
    render,
    get_value_store,
)


def get_str(field: str, data: Mapping[str: object]) -> str | None:
    return str(data[field]) if data.get(field) is not None else None


def get_bool(field: str, data: Mapping[str: object]) -> bool | None:
    return bool(data[field]) if data.get(field) is not None else None


def get_int(field: str, data: Mapping[str: object]) -> bool | None:
    try:
        return int(data[field]) if data.get(field) is not None else None
    except ValueError:
        return None


@dataclass(frozen=True)
class SSLLabsEndpoint:
    ip_address: str | None
    server_name: str | None
    status_message: str | None
    grade: str | None
    grade_trust_ignored: str | None
    has_warnings: bool | None
    is_exceptional: bool | None
    progress: int | None
    duration: int | None
    delegation: int | None
    statusDetails: str | None
    statusDetailsMessage: str | None

    @classmethod
    def parse(cls, end_point: Mapping):
        return cls(
            ip_address=get_str('ipAddress', end_point),
            server_name=get_str('serverName', end_point),
            status_message=get_str('statusMessage', end_point),
            grade=get_str('grade', end_point),
            grade_trust_ignored=get_str('gradeTrustIgnored', end_point),
            has_warnings=get_bool('hasWarnings', end_point),
            is_exceptional=get_bool('isExceptional', end_point),
            progress=get_int('progress', end_point),
            duration=get_int('duration', end_point),
            delegation=get_int('delegation', end_point),
            statusDetails=get_str('statusDetails', end_point),
            statusDetailsMessage=get_str('statusDetailsMessage', end_point),
        )


@dataclass(frozen=True)
class SSLLabsHost:
    host: str
    port: int
    protocol: str
    is_public: bool
    status: str
    start_time: int
    test_time: int | None
    engine_version: str
    criteria_version: str
    status_message: str | None
    cache_expiry_time: int | None
    from_agent_cache: bool | None
    end_points: Sequence[SSLLabsEndpoint] | None
    errors: Sequence[str] | None

    @classmethod
    def parse(cls, ssl_host):
        return cls(
            host=get_str('host', ssl_host),
            port=get_int('port', ssl_host),
            protocol=get_str('protocol', ssl_host),
            is_public=get_bool('isPublic', ssl_host),
            status=get_str('status', ssl_host),
            start_time=get_int('startTime', ssl_host),
            test_time=get_int('testTime', ssl_host),
            engine_version=get_str('engineVersion', ssl_host),
            criteria_version=get_str('criteriaVersion', ssl_host),
            status_message=get_str('statusMessage', ssl_host),
            cache_expiry_time=get_int('cacheExpiryTime', ssl_host),
            from_agent_cache=get_bool('from_agent_cache', ssl_host),
            end_points=[SSLLabsEndpoint.parse(endpoint) for endpoint in ssl_host.get('endpoints', [])],
            errors=[str(error) for error in ssl_host.get('errors', [])] if ssl_host.get('errors') else None,
        )


SECTION = Mapping[str: SSLLabsHost]


# _CMK_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%m %Z'


def parse_ssllabs_grade(string_table) -> SECTION | None:
    try:
        data = json_loads(string_table[0][0])
    except JSONDecodeError:
        return

    ssl_hosts = {host['host']: SSLLabsHost.parse(host) for host in data if host.get('host') is not None}
    return ssl_hosts


def discovery_ssllabs_grade(section: SECTION) -> DiscoveryResult:
    for ssl_host in section:
        yield Service(item=ssl_host)


def check_grade(score: Tuple, grade: str, name: str, notice_only: bool) -> Result:
    re_ok = re_compile(score[0])
    re_warn = re_compile(score[1])
    re_crit = re_compile(score[2])

    if re_match(re_ok, grade):
        state = State.OK
    elif re_match(re_warn, grade):
        state = State.WARN
    elif re_match(re_crit, grade):
        state = State.CRIT
    else:
        state = State.UNKNOWN

    message = f'{name} Grade: {grade}'.strip()
    if notice_only:
        yield Result(state=state, notice=message)
    else:
        yield Result(state=state, summary=message)


def check_grades(params: Mapping[str: any], ssl_host: SSLLabsHost, value_store):
    grades = list(set([end_point.grade for end_point in ssl_host.end_points if end_point.grade is not None]))
    if len(grades) == 1:
        yield from check_grade(score=params['score'], name='', grade=grades[0], notice_only=False)
        if (last_grade := value_store.get(ssl_host.host)) is not None:
            yield Result(state=State.OK, summary=f'Last grade: {last_grade}')
        value_store[ssl_host.host] = grades[0]
    elif len(grades) == 0:
        yield Result(state=State(params.get('no_grade', 1)), notice=f'No grade information found')
    else:
        end_points: Sequence[SSLLabsEndpoint] = ssl_host.end_points
        for end_point in end_points:
            name = f'{end_point.server_name}/{end_point.ip_address}'
            last_grade = value_store.get(name)
            if end_point.grade is not None:
                yield from check_grade(
                    score=params['score'],
                    name=name,
                    grade=end_point.grade,
                    notice_only=True,
                )
                yield Result(state=State.OK, notice=f'{name} last grade: {last_grade}')
                value_store[name] = end_point.grade
            elif last_grade is not None:
                yield from check_grade(
                    score=params['score'],
                    name=f'{name} Last',
                    grade=last_grade,
                    notice_only=True,
                )


def check_has_warning(params: Mapping[str: any], end_points: Sequence[SSLLabsEndpoint]):
    has_warnings = list(set([
        end_point.has_warnings for end_point in end_points if end_point.has_warnings is not None
    ]))
    if len(has_warnings) == 1 and has_warnings[0] is True:
        yield Result(state=State(params.get('has_warnings', 1)), notice=f'Has warnings')
    else:
        for end_point in end_points:
            name = f'{end_point.server_name}/{end_point.ip_address}'
            if end_point.has_warnings is True:
                yield Result(state=State(params.get('has_warnings', 1)), notice=f'{name}: has warnings')


def check_is_exceptional(params: Mapping[str: any], end_points: Sequence[SSLLabsEndpoint]):
    is_exceptional = list(set([
        end_point.is_exceptional for end_point in end_points if end_point.is_exceptional is not None
    ]))
    if len(is_exceptional) == 1 and is_exceptional[0] is not True:
        yield Result(state=State(params.get('is_exceptional', 1)), notice=f'Is not exceptional')
    else:
        for end_point in end_points:
            name = f'{end_point.server_name}/{end_point.ip_address}'
            if end_point.has_warnings is True:
                yield Result(state=State(params.get('is_exceptional', 1)), notice=f'{name}: is not exceptional')


def check_status(params: Mapping[str: any], end_points: Sequence[SSLLabsEndpoint]):
    for end_point in end_points:
        name = f'{end_point.server_name}/{end_point.ip_address}'

        if end_point.status_message.lower() not in ['ready', 'in progress', 'pending']:
            yield Result(state=State.WARN, notice=f'Status {name}: {end_point.status_message}')


def check_ssllabs_grade(item: str, params: Mapping[str: any], section: SECTION) -> CheckResult:
    try:
        ssl_host: SSLLabsHost = section[item]
    except KeyError:
        yield Result(state=State.UNKNOWN, summary=f'Item not found in monitoring data. ({str(section)})')
        return None

    if ssl_host.errors:
        for error in ssl_host.errors:
            yield Result(state=State.WARN, notice=error)

    value_store = get_value_store()

    match ssl_host.status:
        case 'READY':
            levels_upper = None
            if params.get('age') is not None:
                warn, crit = params.get('age')
                levels_upper = (warn * 86400, crit * 86400)  # change to days

            yield from check_levels(
                value=now_time() - (ssl_host.test_time / 1000),
                label='Last tested',
                render_func=render.timespan,
                levels_upper=levels_upper,
                # notice_only=True,
            )
            yield from check_grades(params, ssl_host, value_store)
            yield from check_has_warning(params, ssl_host.end_points)
            yield from check_is_exceptional(params, ssl_host.end_points)
            yield from check_status(params, ssl_host.end_points)

        case 'DNS':
            yield Result(state=State(params.get('state_dns', 0)), summary=f'DNS: {ssl_host.status_message}')
            yield Result(
                state=State.OK,
                summary=f'Started {render.timespan(now_time() - (ssl_host.start_time / 1000))} before'
            )
        case 'ERROR':
            yield Result(state=State(params.get('state_error', 1)), notice=f'Error: {ssl_host.status_message}')
            if ssl_host.cache_expiry_time:
                yield Result(
                    state=State.OK,
                    notice=f'Cache expiry time: {render.datetime(ssl_host.cache_expiry_time / 1000)}'
                )
        case 'IN_PROGRESS':
            yield Result(
                state=State(params.get('state_in_progress', 0)),
                summary=f'Test is in progress, started '
                        f'{render.timespan(now_time() - (ssl_host.start_time / 1000))} before'
            )
            yield from check_grades(params, ssl_host, value_store)
            yield from check_has_warning(params, ssl_host.end_points)
            yield from check_is_exceptional(params, ssl_host.end_points)
            yield from check_status(params, ssl_host.end_points)
        case None:
            pass
        case _:
            yield Result(state=State.UNKNOWN, notice=f'Unknown test status: {ssl_host.status}')

    yield Result(state=State.OK, notice=f'For full details go to https://www.ssllabs.com/ssltest/analyze.html?d={item}')

    if params.get('details'):
        yield Result(state=State.OK, notice=f'\nHost details')
        yield Result(state=State.OK, notice=f'Host: {ssl_host.host}')
        yield Result(state=State.OK, notice=f'Port: {ssl_host.port}')
        yield Result(state=State.OK, notice=f'Protocol: {ssl_host.protocol}')
        yield Result(state=State.OK, notice=f'Start Time: {render.datetime(ssl_host.start_time / 1000)}')
        if ssl_host.test_time is not None:
            yield Result(state=State.OK, notice=f'Test Time: {render.datetime(ssl_host.test_time / 1000)}')
        yield Result(state=State.OK, notice=f'Engine version: {ssl_host.engine_version}')
        yield Result(state=State.OK, notice=f'Criteria version: {ssl_host.criteria_version}')
        yield Result(state=State.OK, notice=f'Status: {ssl_host.status}')
        if ssl_host.from_agent_cache is not None:
            yield Result(state=State.OK, notice=f'From agent cache: {ssl_host.from_agent_cache}')
        else:
            yield Result(state=State.OK, notice=f'Live data')

        if ssl_host.end_points:
            yield Result(state=State.OK, notice=f'\nEndpoints')
        for end_point in ssl_host.end_points:
            yield Result(state=State.OK, notice=f'Server name: {end_point.server_name}')
            yield Result(state=State.OK, notice=f'IP-Address: {end_point.ip_address}')
            yield Result(state=State.OK, notice=f'Status Message: {end_point.status_message}')
            if end_point.grade is not None:
                yield Result(state=State.OK, notice=f'Grade: {end_point.grade}')

            name = f'{end_point.server_name}/{end_point.ip_address}'
            if (last_grade := value_store.get(name)) is not None:
                yield Result(state=State.OK, notice=f'Last grade: {last_grade}')

            if end_point.grade_trust_ignored is not None:
                yield Result(state=State.OK, notice=f'Grade Trust Ignored: {end_point.grade_trust_ignored}')
            if end_point.has_warnings is not None:
                yield Result(state=State.OK, notice=f'has warnings: {end_point.has_warnings}')
            if end_point.is_exceptional is not None:
                yield Result(state=State.OK, notice=f'is exceptional: {end_point.is_exceptional}')
            if end_point.progress is not None:
                yield Result(state=State.OK, notice=f'progress: {end_point.progress}')
            if end_point.duration is not None:
                yield Result(state=State.OK, notice=f'duration: {render.timespan(end_point.duration / 1000)}s')
            yield Result(state=State.OK, notice=f'delegation: {end_point.delegation}')
            yield Result(state=State.OK, notice=f'\n')


register.agent_section(
    name="ssllabs_grade",
    parse_function=parse_ssllabs_grade,
)

register.check_plugin(
    name='ssllabs_grade',
    service_name='SSL Labs %s',
    discovery_function=discovery_ssllabs_grade,
    check_function=check_ssllabs_grade,
    check_default_parameters={
        "score": ("A", "B|C", "D|E|F|M|T"),
    },
    check_ruleset_name='ssllabs_grade'
)
