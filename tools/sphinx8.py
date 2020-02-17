#!/usr/bin/env python

"""
Sphinx documentation style checker.

This is a very thin wrapper around doc8, that adds support for sphinx-specific
RST directives.

NOTE: We require sphinx>1.5 in order to avoid automatically registering all
directives when any of the directives modules are imported.
"""

#  The MIT License (MIT)
#
#  Copyright (c) 2019 László Hegedűs
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys

import doc8.main
import sphinx.directives
import sphinx.directives.code
import sphinx.directives.patches


def main():
    # NOTE: Registering sphinx.directives.other causes a failure in parsing
    # later.
    sphinx.directives.setup(None)
    sphinx.directives.code.setup(None)
    sphinx.directives.patches.setup(None)
    return doc8.main.main()


if __name__ == "__main__":
    sys.exit(main())
