#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voaAreaPlotgui.py
#
# Copyright (c) 2009 J.Watson
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

import sys
import zipfile
from io import BytesIO

from .voaFile import VOAFile

class VGZArchive:

    def __init__(self, filename):
        # TODO if file exists
        with zipfile.ZipFile(filename, 'r') as vgzip:
            self.file_list = vgzip.namelist()
            self.voa_filename = next(fn for fn in self.file_list if fn.endswith('.voa'))
            voa_content = vgzip.read(self.voa_filename)
            print(voa_content)
        self.vf = VOAFile(BytesIO(voa_content))
        print("done init")


    def get_num_plots(self):
        print("Number of plots: {:d}".format(self.vf.get_num_plots()))
        return self.vf.get_num_plots()


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print('Usage: vgzArchive archive_name')
        sys.exit(2)
    app = VGZArchive(sys.argv[-1])
    print("Number of plots: {:d}".format(app.get_num_plots))
