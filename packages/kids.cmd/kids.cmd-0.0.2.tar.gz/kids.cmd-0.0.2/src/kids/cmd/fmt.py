# -*- coding: utf-8 -*-

from kids.data.format import mk_fmt

import termcolor


Ansicolor = lambda color, attrs=None: mk_fmt(
    lambda v, c: termcolor.colored(
        v, c["color"],
        attrs=c.get("attrs", {}))
    )(color=color, attrs=attrs)

Printf = lambda pattern: mk_fmt(
    lambda v, c: pattern % v
    )(pattern)


ConstString = lambda output: mk_fmt(
    lambda v, c: output
    )(output=output)

empty = ConstString("")
