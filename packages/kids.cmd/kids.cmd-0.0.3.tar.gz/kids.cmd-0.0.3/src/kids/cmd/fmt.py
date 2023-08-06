# -*- coding: utf-8 -*-

from kids.data.format import mk_fmt
from kids.ansi import aformat

Ansicolor = lambda color, attrs=None: mk_fmt(
    lambda v, c: aformat(
        v, fg=c["fg"],
        attrs=c.get("attrs", {}))
    )(color=color, attrs=attrs)


Printf = lambda pattern: mk_fmt(
    lambda v, c: pattern % v
    )(pattern)


ConstString = lambda output: mk_fmt(
    lambda v, c: output
    )(output=output)


empty = ConstString("")
