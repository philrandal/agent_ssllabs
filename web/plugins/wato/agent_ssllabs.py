#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#


from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
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

from cmk.gui.plugins.wato.datasource_programs import (
    RulespecGroupDatasourceProgramsOS,
)


def _valuespec_special_agents_ssllabs():
    return Dictionary(
        elements=[
            ('sslhosts',
             ListOfStrings(
                 title=_('SSL hosts to check'),
                 orientation='vertical',
                 allow_empty=False,
             )
             ),
            ('timeout',
             Integer(
                 title=_('Connect Timeout'),
                 help=_('The network timeout in seconds when communicating via HTTPS. '
                        'The default is 60 seconds.'),
                 default_value=60,
                 minvalue=1,
                 unit=_('seconds')
             )
             ),
            ('proxy',
             TextAscii(
                 title=_('proxy server, if required'),
                 help=_('proxy in the format: https://ip-addres|servername:port'),
             ),
             ),
            ('publishresults',
             FixedValue(
                 'on',
                 title=_('Publish results'),
                 totext=_('Results will be published'),
                 help=_('By default test results will not be published. If you enable this option the test'
                        ' results will by public visible on https://www.ssllabs.com/ssltest'),
                 default_value='off',
             )),
            ('maxage',
             Integer(
                 title=_('Max Age for ssllbas.com cache'),
                 help=_('Maximum report age, in hours, if retrieving from "ssllabs.com" cache. '
                        'After this time a new test will by initiated. The default (and minimum) is 167 hours'),
                 default_value=167,
                 minvalue=167,
             )),
        ],
        title=_('Qualys SSL Labs server test'),
        help=_('This rule selects the ssllabs agent, which fetches SSL Server status from api.ssllabs.com.'
               'For more details about the SSL server check see https://www.ssllabs.com/ssltest/index.html.'
               'For mor information about the SSL Labs API see: '
               'https://github.com/ssllabs/ssllabs-scan/blob/master/ssllabs-api-docs-v3.md.'),
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsOS,
        name='special_agents:ssllabs',
        valuespec=_valuespec_special_agents_ssllabs,
    ))
