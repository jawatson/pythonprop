#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voaAreaPlotgui.py
#
# Copyright (c) 2016 J.Watson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import os
import zipfile

def get_voa_filename(zname):
    with zipfile.ZipFile(zname, 'r') as vgzip:
        file_list = vgzip.namelist()
        return next(fn for fn in file_list if fn.endswith('.voa'))

def get_base_filename(zname):
    return os.path.splitext(get_voa_filename(zname))[0]
