#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# prepare-basic-pkg-info.py --- Write basic-pkg-info.rst with contents
#                               extracted from the canonical README.rst
#
# Copyright (c) 2015, Florent Rougon
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
import re
import locale


def main():
    locale.setlocale(locale.LC_ALL, '')

    with open(sys.argv[1], "r", encoding="utf-8") as ifile:
        contents = ifile.read()

    mo = re.search(r"\n\n\.\. _end-of-intro:\n\n(.*)", contents, re.DOTALL)
    assert mo, mo

    # Improve the markup using Sphinx's 'note' directive. We include enough
    # context to be reasonably sure we don't replace something else than the
    # expected text.
    rest = re.sub(r"^Note:\n\n( +The ``Makefile`` uses a Python script)",
                  r".. note::\n\n\1", mo.group(1), 1, re.MULTILINE)

    with open(sys.argv[2], "w", encoding="utf-8") as ofile:
        ofile.write(rest)

    sys.exit(0)

if __name__ == "__main__": main()
