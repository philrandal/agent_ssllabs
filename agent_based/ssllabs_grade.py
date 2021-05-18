#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# 2015 Karsten Schoeke karsten.schoeke@geobasis-bb.de
#
# 2021-05-15: rewritten for CMK 2.0 by thl-cmk[at]outlook[dot]com
#
#
# Example output from agent:
# servername;status;time;agent_state;last_grade_result
# <<<ssllabs_grade:sep(0)>>>
# server1.de;A+;1435565830118;0;A+
# server2.de;A;1435565830118;0;B
# <<<<>>>>


import time, re

from typing import Dict, NamedTuple, Optional

from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    DiscoveryResult,
    CheckResult,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Service,
    State,
    Result,
    get_value_store,
)


class SSLLabsGrade(NamedTuple):
    lastcheck: str
    time_diff: int
    grade: Optional[str]
    agent_state: Optional[int]
    status_detail: str


def parse_ssllabs_grade(string_table):
    ssl_hosts = {}

    for line in string_table:
        line = line[0].split(';')
        if len(line) == 5:
            ssl_host, status_detail, lastcheck, agent_state, grade = line
            lastcheck = time.strftime("%d.%m.%Y %H:%M", time.localtime(int(lastcheck[:10])))
            time_diff = int(time.time() - int(line[2][:10]))
            ssl_hosts.update({ssl_host: SSLLabsGrade(
                lastcheck=lastcheck,
                time_diff=time_diff,
                grade=grade,
                agent_state=int(agent_state),
                status_detail=status_detail
            )})
        if len(line) == 4:
            ssl_host, status_detail, lastcheck, agent_state = line
            lastcheck = time.strftime("%d.%m.%Y %H:%M", time.localtime(int(lastcheck[:10])))
            time_diff = int(time.time() - int(line[2][:10]))
            ssl_hosts.update({ssl_host: SSLLabsGrade(
                lastcheck=lastcheck,
                time_diff=time_diff,
                grade=None,
                agent_state=None,
                status_detail=status_detail
            )})

    return ssl_hosts


def discovery_ssllabs_grade(section: Dict) -> DiscoveryResult:
    for ssl_host in section.keys():
        yield Service(item=ssl_host)


def check_ssllabs_grade(item, params, section: Dict[str, SSLLabsGrade]) -> CheckResult:
    #value_store = get_value_store()
    #print(f'value_store: {value_store}')
    #if not value_store[item][0] == 'last_run':
    #    value_store[item] = ('last_run', {'grade': 'A+'})
    #grade = value_store[item][1].get('grade')
    #print(f'value_store: {grade}')

    try:
        ssllabsgrade = section.get(item)
    except KeyError:
        return None

    ok, warn, crit = params["score"]
    warn_last_run, crit_last_run = params["age"]
    re_ok = re.compile(ok)
    re_warn = re.compile(warn)
    re_crit = re.compile(crit)
    re_error = re.compile('(HTTP|JSON|unknow)')  # API Errors

    if ssllabsgrade.agent_state == 0:  # test done
        if re_crit.match(ssllabsgrade.grade):
            state = State.CRIT
        elif re_warn.match(ssllabsgrade.grade):
            state = State.WARN
        elif re_ok.match(ssllabsgrade.grade):
            state = State.OK
        else:
            state = State.UNKNOWN
        yield Result(state=state, summary=f'Grade "{ssllabsgrade.status_detail}"')

        if ssllabsgrade.time_diff > crit_last_run:
            state = State.CRIT
        elif ssllabsgrade.time_diff > warn_last_run:
            state = State.WARN
        else:
            state = State.OK
        yield Result(state=state, summary=f'Last check at {ssllabsgrade.lastcheck}')
    elif ssllabsgrade.agent_state == 1:  # test in progress
        state = State.WARN
        yield Result(state=state, summary=f'Server check is in progress, status was "{ssllabsgrade.status_detail}"')
    elif ssllabsgrade.agent_state == 2:  # API error
        state = State.CRIT
        yield Result(state=state, summary=f'API error, status was "{ssllabsgrade.status_detail}"')
    else:  # unknown error
        state = State.UNKNOWN
        yield Result(state=state,
                     summary=f'Server check status was "{ssllabsgrade.status_detail}", last check at {ssllabsgrade.lastcheck}')

    yield Result(state=State.OK, notice=f'For details go to https://www.ssllabs.com/ssltest/analyze.html?d={item}')


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
        "age": (604800, 864000),
    },
    check_ruleset_name='ssllabs_grade'
)
