#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# parse_config.py --- Sample program using CondConfigParser
#
# Copyright (c) 2014, 2015, Florent Rougon
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of the CondConfigParser Project.

import sys
import locale
from pprint import pformat

from condconfigparser import RawConditionalConfig


def printTitle(title, width=79, char="*"):
    lines = [ char * width,
              char + title.center(width - 2) + char,
              char * width ]

    print(*lines, sep="\n")


def parseConfig(inputFile, context):
    printTitle(inputFile)

    with open(inputFile, "r", encoding="utf-8") as f:
        config = RawConditionalConfig(f, extvars=context.keys())
    # At this point, CondConfigParser has already checked that the external
    # variables listed in 'extvars' are enough to allow evaluation of all
    # expressions (variable assignments and predicates) contained in the
    # configuration file given by 'inputFile'.
    variables, applicableConfig = config.eval(context)
    print(pformat(variables), pformat(applicableConfig), sep="\n\n")

def main():
    locale.setlocale(locale.LC_ALL, '')

    parseConfig("config1", {"extvar1": "quux",
                            "extvar2": [12, 'abc', [False, 'def']]})
    print("\n")
    parseConfig("config2", {"fruit_of_the_day": "mango",
                            "fruit_status": "fine"})

    sys.exit(0)

if __name__ == "__main__": main()
