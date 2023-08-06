# -*- coding: utf-8 -*-

from __future__ import print_function

try:
    ## Windows implementation
    import msvcrt
    _getch = msvcrt.getch

except ImportError:

    ## Linux/Unix implementation
    import tty
    import sys
    import termios

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def getch():
    char = _getch()
    if char == '\x03':
        raise KeyboardInterrupt
    elif char == '\x04':
        raise EOFError
    return char


def raw_char(prompt=""):
    char = ""
    while not char:
        print(prompt, end="")
        char = getch().strip()
        print(char)
    return char
