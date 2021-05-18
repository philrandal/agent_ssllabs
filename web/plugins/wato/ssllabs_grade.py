#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#
# 2015 Karsten Schoeke karsten.schoeke@geobasis-bb.de
#
# 2021-05-15: rewritten for CMK 2.0 by thl-cmk[at]outlook[dot]com
#

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
    Age,
    Tuple,
    RegExpUnicode,
    RegExp,
)

from cmk.gui.plugins.wato import (
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
                 Age(title=_('Warning at'), default_value=604800, minvalue=604800),
                 Age(title=_('Critical at'), default_value=864000, minvalue=691200),
             ]
         ),
         ),
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
             ]
         ),
         ),
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
