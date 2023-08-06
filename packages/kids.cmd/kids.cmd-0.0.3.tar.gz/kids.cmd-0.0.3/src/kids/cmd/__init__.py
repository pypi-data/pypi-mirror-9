# -*- coding: utf-8 -*-

from .cmd import BaseCommand, cmd, register, run
from .msg import warn, err, die
from .input import raw_char, getch
from .menu import menu


def check_root():
    if not os.geteuid() == 0:
        raise OSError("\nYou must be root to run this script\n")

