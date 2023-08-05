# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

PY2 = sys.version_info[0] == 2

if not PY2:
    unichr = chr
    range_type = range
    text_type = str
    string_types = (str,)
else:
    unichr = unichr
    text_type = unicode  # @UndefinedVariable
    range_type = xrange  # @UndefinedVariable
    string_types = (str, unicode)  # @UndefinedVariable

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
