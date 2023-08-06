#!/usr/bin/env python
"""
Copyright (c) 2013-2015 Fraunhofer FKIE

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of the Fraunhofer organization nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import os
import re
import tempfile

def word_split(s):
    ws = re.compile(r"(\W|_)+|(?<=[^A-Z])(?=[A-Z])|(?<=\w)(?=[A-Z][a-z])")
    mo = ws.search(s)
    result = []
    while mo:
        result.append(s[:mo.start()].lower())
        s = s[mo.end():]
        mo = ws.search(s)
    result.append(s.lower())
    return result

try:
    from itertools import zip_longest
except ImportError:
    def zip_longest(*args):
        return map(None, *args)


def write_atomic(filepath, data):
    fd, filepath_tmp = tempfile.mkstemp(prefix=os.path.basename(filepath) + ".tmp.", dir=os.path.dirname(filepath))
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.close()
    try:
        os.rename (filepath_tmp, filepath)
    except OSError:
        try:
            os.unlink(filepath)
        except OSError:
            pass
        try:
            os.rename(filepath_tmp, filepath)
        except OSError:
            os.unlink(filepath_tmp)


# Python 3 compatibility without sacrificing the speed gain of iteritems in Python 2
try:
    iteritems = dict.iteritems
except AttributeError:
    iteritems = dict.items
