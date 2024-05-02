#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2024-04-29
# File  : ssllabs.py (wato special agent)
#

# based on the ssllabs plugin from Karsten Schoeke karsten.schoeke@geobasis-bb.de
# see https://exchange.checkmk.com/p/ssllabs

# 2024-05-01: modified for CMK 2.2.x

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    TextAscii,
    ListOfStrings,
    FixedValue,
)

from cmk.gui.plugins.wato.special_agents.common import RulespecGroupDatasourceProgramsApps


def _valuespec_special_agents_ssllabs():
    return Dictionary(
        elements=[
            ('ssl_hosts',
             ListOfStrings(
                 title=_('SSL hosts to check'),
                 orientation='vertical',
                 allow_empty=False,
                 size=50,
                 empty_text='www.checkmk.com',
                 max_entries=10,
                 help=_(
                     'List of server names to check. Add the host names without "http(s)://". Ie: www.checkmk.com. '
                     'The list is limited to 10 entries. If you need more than 10 entries create another rule.'
                 ),
             )),
            ('timeout',
             Integer(
                 title=_('Connect Timeout'),
                 help=_(
                     'The network timeout in seconds when communicating via HTTPS. The default is 30 seconds.'
                 ),
                 default_value=30,
                 minvalue=1,
                 unit=_('seconds')
             )),
            ('proxy',
             TextAscii(
                 title=_('proxy server, if required'),
                 help=_('proxy in the format: https://ip-addres|servername:port'),
             )),
            ('publish_results',
             FixedValue(
                 value='on',
                 title=_('Publish results'),
                 totext=_('Results will be published'),
                 help=_(
                     'By default test results will not be published. If you enable this option the test'
                     ' results will by public visible on https://www.ssllabs.com/ssltest'
                 ),
                 default_value='off',
             )),
            ('max_age',
             Integer(
                 title=_('Max Age for ssllbas.com cache'),
                 help=_(
                     'Maximum report age, in hours, if retrieving from "ssllabs.com" cache. '
                     'After this time a new test will by initiated. The default (and minimum) is 1 Day'
                 ),
                 default_value=1,
                 minvalue=1,
                 unit=_('Days')
             )),
        ],
        title=_('Qualys SSL Labs scan'),
        help=_(
            'This rule selects the ssllabs agent, which fetches SSL Server status from api.ssllabs.com.'
            'For more details about the SSL server check see https://www.ssllabs.com/ssltest/index.html.'
            'For mor information about the SSL Labs API see: '
            'https://github.com/ssllabs/ssllabs-scan/blob/master/ssllabs-api-docs-v3.md.'
        ),
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsApps,
        name='special_agents:ssllabs',
        valuespec=_valuespec_special_agents_ssllabs,
    ))
