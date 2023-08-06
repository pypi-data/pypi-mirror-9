# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
from kids.ansi import aformat


def info(msg):
    print(aformat("Info: ", fg='green') + msg,
          file=sys.stderr)


def warn(msg):
    print(aformat("Warning: ", fg='yellow') + msg,
          file=sys.stderr)


def err(msg):
    print(aformat("Error: ", fg='red',
                  attrs=['bold', ]) + msg,
          file=sys.stderr)


def die(msg=None, errlvl=1):
    if msg:
        sys.stderr.write(str(
            aformat("Fatal: ", fg='red',
                    attrs=['bold', ]) +
            ("%s\n" % msg)))
    sys.exit(errlvl)
