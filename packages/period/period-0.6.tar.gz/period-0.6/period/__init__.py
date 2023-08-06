# -*- coding: utf-8 -*-
import pkg_resources

__version__ = "unknown"

try:
    __version__ = pkg_resources.resource_string("period",
                                                "RELEASE-VERSION").strip()
except IOError:
    __version__ = "0.0.0"


from period.main import PeriodParser, PeriodSyntax, Stack, in_period, is_holiday
