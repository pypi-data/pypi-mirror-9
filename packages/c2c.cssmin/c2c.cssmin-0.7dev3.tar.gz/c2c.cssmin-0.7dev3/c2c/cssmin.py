# -*- coding: utf-8 -*-

# Copyright (c) 2011-2014, Camptocamp SA
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.

import re
import os

from os.path import relpath
import cssmin
from argparse import ArgumentParser


def relocate_urls(css, src, dest):
    """ Relocate all relative urls """
    # matches relative files only
    regex = re.compile(r"url\(\s?[\'\"]?([^:'\"]+)[\'\"]?\s?\)")
    return regex.sub(relative(src, dest), css)


def relative(src, dest):
    """ Return the relocator function """
    srcdir = os.path.dirname(src)
    destdir = os.path.dirname(dest)

    def _relative(m):
        if m is not None:
            abspath = os.path.normpath(os.path.join(srcdir, m.group(1)))
            # force '/' as path separator
            return "url('%s')" % "/".join(relpath(abspath, destdir).split(os.sep))

    return _relative


def main():
    parser = ArgumentParser(
        description="Minify and aggregate CSS"
    )

    parser.add_argument("--compress", "-c", action="store_true", help="minify the CSS")
    parser.add_argument("output", metavar="OUTPUT_FILE", help="the output file")
    parser.add_argument(
        "inputs", metavar="INPUT_FILE", nargs="+", help="the input files"
    )

    options = parser.parse_args()

    dir = os.path.dirname(options.output)
    if not os.path.exists(dir):
        os.makedirs(dir)
    output = open(options.output, "wt")
    for f in options.inputs:
        css = relocate_urls(open(f).read(), f, options.output)
        if options.compress:
            output.write(cssmin.cssmin(css, wrap=options.wrap))
        else:
            output.write(css)
    output.close()

    print("Merging %s to %s" % (options.inputs, options.output))
