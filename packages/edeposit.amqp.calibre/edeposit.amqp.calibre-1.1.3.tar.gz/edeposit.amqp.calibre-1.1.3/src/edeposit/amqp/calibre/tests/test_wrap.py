#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# This file is for py.test framework
#
# Imports =====================================================================
import sys
import time
from textwrap import wrap

sys.path.insert(0, "../../")
import calibre


# Functions & classes =========================================================
def get_text_block():
    out = ""
    pool = "qwertzuiopasdfghjklyxcvbnmQWERTZUIOPASDFGHJKLYXCVBNM"

    for i in range(1024*20):  # 100kB of text without spaces
        out += pool[i % len(pool)]

    return out


if __name__ == "__main__":
    print "Measuring textwrap.wrap().."
    t1 = time.time()
    "\n".join(wrap(get_text_block(), 80))
    t2 = time.time()

    print t2 - t1, "seconds"

    print "Measuring own wrap().."
    t1 = time.time()
    out = calibre.calibre._wrap(get_text_block(), 79)
    t2 = time.time()
    print t2 - t1, "seconds"

    print out
