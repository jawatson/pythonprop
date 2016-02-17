#!/usr/bin/env python
# -*- Mode: Python; py-indent-offset: 4 -*-
# vim: tabstop=4 shiftwidth=4 expandtab
#
# Copyright (C) 2010 Red Hat, Inc., John (J5) Palmieri <johnp@redhat.com>
#
# The original file has been tailored to printing voacap output files
# incorporating hard-coded page breaks.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA

# The original version of this file may be found at;
# https://github.com/GNOME/pygobject/blob/master/demos/gtk-demo/demos/printing.py

import gi
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, GLib, Pango, PangoCairo
import math
import os


class VOAOutFilePrinter:
    HEADER_HEIGHT = 10 * 72 / 25.4
    HEADER_GAP = 3 * 72 / 25.4

    def __init__(self, out_file_path):
        self.operation = Gtk.PrintOperation()
        print_data = {'filename': out_file_path,
                      'font_size': 10.0,
                      'lines': None,
                      'num_pages': 0
                     }

        self.operation.connect('begin-print', self.begin_print, print_data)
        self.operation.connect('draw-page', self.draw_page, print_data)
        self.operation.connect('end-print', self.end_print, print_data)

        self.operation.set_use_full_page(False)
        self.operation.set_unit(Gtk.Unit.POINTS)
        self.operation.set_embed_page_setup(True)

        settings = Gtk.PrintSettings()

        dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if dir is None:
            dir = GLib.get_home_dir()
        if settings.get(Gtk.PRINT_SETTINGS_OUTPUT_FILE_FORMAT) == 'ps':
            ext = '.ps'
        elif settings.get(Gtk.PRINT_SETTINGS_OUTPUT_FILE_FORMAT) == 'svg':
            ext = '.svg'
        else:
            ext = '.pdf'
        base_name = os.path.splitext(os.path.basename(out_file_path))[0]
        uri = "file://{:s}/{:s}{:s}".format(dir, base_name, ext)
        settings.set(Gtk.PRINT_SETTINGS_OUTPUT_URI, uri)
        self.operation.set_print_settings(settings)

    def run(self, parent=None):
        result = self.operation.run(Gtk.PrintOperationAction.PRINT_DIALOG,
                    parent)

        if result == Gtk.PrintOperationResult.ERROR:
            message = self.operation.get_error()

            dialog = Gtk.MessageDialog(parent,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CLOSE,
                    message)
            dialog.run()
            dialog.destroy()

        #Gtk.main_quit()

    def begin_print(self, operation, print_ctx, print_data):
        height = print_ctx.get_height() - self.HEADER_HEIGHT - self.HEADER_GAP

        file_path = print_data['filename']
        if not os.path.isfile(file_path):
            raise Exception("file not found: {:s}".format(file_path))

        # in reality you should most likely not read the entire
        # file into a buffer
        source_file = open(file_path, 'r')
        s = source_file.read()
        print_data['pages'] = s.split('\f')
        #print(print_data['pages'])

        print_data['num_pages'] = len(print_data['pages'])

        operation.set_n_pages(print_data['num_pages'])

    def draw_page(self, operation, print_ctx, page_num, print_data):
        cr = print_ctx.get_cairo_context()
        width = print_ctx.get_width()

        cr.move_to(0, self.HEADER_HEIGHT)
        cr.line_to(width, self.HEADER_HEIGHT)
        cr.set_line_width(1)
        cr.stroke()

        layout = print_ctx.create_pango_layout()
        desc = Pango.FontDescription('sans 12')
        layout.set_font_description(desc)

        layout.set_text(print_data['filename'], -1)
        (text_width, text_height) = layout.get_pixel_size()

        if text_width > width:
            layout.set_width(width)
            layout.set_ellipsize(Pango.EllipsizeMode.START)
            (text_width, text_height) = layout.get_pixel_size()

        cr.move_to(0, (self.HEADER_HEIGHT - text_height) / 2)
        PangoCairo.show_layout(cr, layout)

        page_str = "{:d}/{:d}".format(page_num + 1, print_data['num_pages'])
        layout.set_text(page_str, -1)

        layout.set_width(-1)
        (text_width, text_height) = layout.get_pixel_size()
        cr.move_to(width - text_width - 4,
                   (self.HEADER_HEIGHT - text_height) / 2)
        PangoCairo.show_layout(cr, layout)

        layout = print_ctx.create_pango_layout()

        desc = Pango.FontDescription('monospace')
        desc.set_size(print_data['font_size'] * Pango.SCALE)
        layout.set_font_description(desc)

        cr.move_to(0, self.HEADER_HEIGHT + self.HEADER_GAP)
        font_size = print_data['font_size']

        for line in (print_data['pages'][page_num]).split('\n'):
            layout.set_text(line, -1)
            PangoCairo.show_layout(cr, layout)
            cr.rel_move_to(0, font_size)

    def end_print(self, operation, print_ctx, print_data):
        pass


def main(demoapp=None):
    app = VOAOutFilePrinter('/home/jwatson/itshfbc/run/voacapx.out')
    GLib.idle_add(app.run, demoapp)
    Gtk.main()

if __name__ == '__main__':
    main()
