#! /usr/bin/env python3
# -*- coding: utf-8 -*-

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

from setuptools import setup, find_packages
import sys
import os
import subprocess
import traceback

setuptools_pkg = "CondConfigParser"
pypkg_name = "condconfigparser"
here = os.path.abspath(os.path.dirname(__file__))

namespace = {}
version_file = os.path.join(here, pypkg_name, "version.py")
with open(version_file, "r", encoding="utf-8") as f:
    exec(f.read(), namespace)
version = namespace["__version__"]


# This function must be run from the root directory of the Git repository.
def run_gitlog_to_changelog(output=None):
    args = [ "gitlog-to-changelog", "--format=%s%n%n%b%n" ]
    try:
        subprocess.check_call(args, stdout=output)
    except os.error:
        print(traceback.format_exc(), file=sys.stderr)

        print("""\
Error (see above for a traceback): unable to run {prg}
================================================={underlining}
Maybe this program is not installed on your system. You can download it from:

  {url}

Note: if you have problems with the infamous shell+Perl crap in the first lines
of that file, you can replace it with a simple shebang line such as
"#! /usr/bin/perl".""".format(
   prg=args[0],
   underlining="=" * len(args[0]),
   url="http://git.savannah.gnu.org/gitweb/?p=gnulib.git;a=blob_plain;"
       "f=build-aux/gitlog-to-changelog"), file=sys.stderr)
        sys.exit(1)


# This function must be run from the root directory of the Git repository.
def generate_changelog(ch_name, write_to_stdout=False):
    print("Converting the Git log into ChangeLog format...", end=' ',
          file=sys.stderr)

    if write_to_stdout:
        run_gitlog_to_changelog()
    else:
        tmp_ch_name = "{0}.new".format(ch_name)

        try:
            with open(tmp_ch_name, "w", encoding="utf-8") as tmp_ch:
                run_gitlog_to_changelog(output=tmp_ch)

            os.rename(tmp_ch_name, ch_name)
        finally:
            if os.path.exists(tmp_ch_name):
                os.unlink(tmp_ch_name)

    print("done.", file=sys.stderr)


def do_setup():
    with open("README.rst", "r", encoding="utf-8") as f:
        long_description = f.read()

    setup(
        name=setuptools_pkg,
        version=version,

        description="Python library for parsing configuration files with "
                    "conditionals",
        long_description=long_description,

        # The project's main homepage
        url="http://people.via.ecp.fr/~flo/projects/{}/".format(setuptools_pkg),

        # Author details
        author="Florent Rougon",
        author_email='f.rougon@free.fr',

        # Choose your license
        license='2-clause BSD',

        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        keywords=\
            'configuration file parsing parser conditionals variables lists',

        packages=find_packages(exclude=['docs', 'example', 'dev-tools']),
        include_package_data=True,

        install_requires=[],
        test_suite="condconfigparser.tests")


def main():
    ch_name = "ChangeLog"
    if os.path.isdir(".git"):
        generate_changelog(ch_name)
    elif not os.path.isfile(ch_name):
        msg = """\
There is no {cl!r} file here and it seems you are not operating from a
clone of the Git repository (no .git directory); therefore, it is impossible to
generate the {cl!r} file from the Git log. Aborting.""".format(cl=ch_name)
        sys.exit(msg)

    do_setup()


if __name__ == "__main__": main()
