#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN -- http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import unicode_literals

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

import sys
from pkg_resources import iter_entry_points

from pyannote.core import T, TStart, TEnd, Transcription
from pyannote.core import Segment, Timeline, Annotation
from core import Episode
from plugin import Plugin

__all__ = [
    'Plugin',
    'Episode',
    'Segment', 'Timeline', 'Annotation',
    'T', 'TStart', 'TEnd', 'Transcription'
]

# plugin_name --> plugin_class
series_plugins = {}

for o in iter_entry_points(group='tvd.series', name=None):

    series = o.name

    plugin = o.load()
    series_plugins[series] = plugin

    setattr(sys.modules[__name__], series, plugin)
    __all__.append(series)
