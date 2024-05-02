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

# based on the ssllabs plugin from Karsten Schoeke karsten.schoeke@geobasis-bb.de
# see https://exchange.checkmk.com/p/ssllabs

#
# 2021-05-15: rewritten for CMK 2.0 by thl-cmk[at]outlook[dot]com
# 2024-05-01: modified for CMK 2.2.x
#             moved to ~/local/lib/check_mk/gui/plugins/wato/check_parameters
# 2024-05-01: changed age to days

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    FixedValue,
    Integer,
    RegExp,
    RegExpUnicode,
    TextAscii,
    Tuple,
    MonitoringState,
)

from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersNetworking,
)


def _parameter_valuespec_ssllabs_grade():
    return Dictionary(elements=[
        ('age',
         Tuple(
             title=_('Maximum age of ssllabs scan'),
             help=_('The maximum age of the last ssllabs check.'),
             elements=[
                 Integer(title=_('Warning at'), default_value=2, minvalue=1),
                 Integer(title=_('Critical at'), default_value=3, minvalue=1),
             ])),
        ('score',
         Tuple(
             title=_('grade level for ssllabs scan'),
             help=_('Put here the Integerttern (regex) for ssllabs grade check level.'),
             elements=[
                 RegExpUnicode(
                     title=_('Pattern (regex) Ok level'),
                     mode=RegExp.prefix,
                     default_value='A',
                 ),
                 RegExpUnicode(
                     title=_('Pattern (regex) Warning level'),
                     mode=RegExp.prefix,
                     default_value='B|C',
                 ),
                 RegExpUnicode(
                     title=_('Pattern (regex) Critical level'),
                     mode=RegExp.prefix,
                     default_value='D|E|F|M|T',
                 ),
             ])),
        ('no_grade',
         MonitoringState(
             title=_('Monitoring state if no grade was found'),
             default_value=1,
             help=_('Set the monitoring state no grade information was found the result. Default is WARN.'),
         )),
        ('has_warnings',
         MonitoringState(
             title=_('Monitoring state if host has warnings'),
             default_value=1,
             help=_('Set the monitoring state if "hasWarnings" in the result is true. Default is WARN.'),
         )),
        ('is_exceptional',
         MonitoringState(
             title=_('Monitoring state if host is not exceptional'),
             default_value=1,
             help=_('Set the monitoring state if "isExceptional" in the result is not true. Default is WARN.'),
         )),
        ('state_dns',
         MonitoringState(
             title=_('Monitoring state if the check is in "DNS resolving" state'),
             default_value=0,
             help=_('Set the monitoring state if the ssllabs scan is in "DNS resolving" state. Default is OK.'),
         )),
        ('state_error',
         MonitoringState(
             title=_('Monitoring state if the check is in "ERROR" state'),
             default_value=1,
             help=_('Set the monitoring state if the ssllabs scan is reporting an "ERROR". Default is WARN.'),
         )),
        ('state_in_progress',
         MonitoringState(
             title=_('Monitoring state if the check is in "IN_PROGRESS" state'),
             default_value=0,
             help=_('Set the monitoring state if the ssllabs scan is "IN_PROGRESS". Default is OK.'),
         )),
        ('details',
         FixedValue(
             value=True,
             title=_('Show result detail in the service details'),
             totext='',
         ))
    ],
        title=_('SSL Server check via ssllabs API'),
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name='ssllabs_grade',
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextAscii(title=_('The FQDN on ssl server to check'), ),
        match_type='dict',
        parameter_valuespec=_parameter_valuespec_ssllabs_grade,
        title=lambda: _('SSL Server via ssllabs API.'),
    ))
