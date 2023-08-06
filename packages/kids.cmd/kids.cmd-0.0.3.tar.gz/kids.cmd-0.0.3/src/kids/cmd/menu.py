# -*- coding: utf-8 -*-

import re

from kids import ansi


def line(line_def, **kwargs):
    """Highlights a character in the line"""
    def replace(s):
        return "(%s)" % ansi.aformat(s.group()[1:], attrs=["bold", ])
    return ansi.aformat(
        re.sub('@.?', replace, line_def),
        **kwargs)


def menu(menu_def):
    return "\n".join(
        "  - %s" % line(line_def, **kwargs)
        for line_def, kwargs in menu_def)
