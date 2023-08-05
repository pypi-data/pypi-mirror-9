#! /usr/bin/env python3

# test.py --- Simple test script for CondConfigParser
#
# Copyright (c) 2014, Florent Rougon
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

import sys, locale
from pprint import pprint, pformat
from condconfigparser import Lexer, Parser, RawConditionalConfig

def main():
    locale.setlocale(locale.LC_ALL, '')

    test = sys.argv[1]
    cfgfile = sys.argv[2]

    with open(cfgfile, "r") as f:
        if test in ("p", "parsetree", "P"):
            lexer = Lexer(f)
            parser = Parser(lexer)
            tree = parser.buildTree()
            if test == "P":
                pprint(tree)
            else:
                print("{:tree}".format(tree))
        elif test in ("t", "tokens"):
            lexer = Lexer(f)
            gen = lexer.tokenGenerator()
            for token in gen:
                print(token)
        elif test in ("c", "configlines"):
            context = {"aircraft": "c172p",
                       "airport": "LFPG",
                       "parking": "XYZ0",
                       "scenarios":
                           ["nimitz_demo", "clemenceau_demo", "balloon_demo"]}

            config = RawConditionalConfig(f, context.keys())
            pprint(config.eval(context))
        else:
            sys.exit("Invalid test identifier: {!r}".format(test))

    sys.exit(0)

if __name__ == "__main__": main()
