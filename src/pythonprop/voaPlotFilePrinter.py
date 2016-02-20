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

""""
printing pngs with python
http://stackoverflow.com/questions/10983739/how-to-composite-multiple-png-into-a-single-png-using-gtk-cairo

"""

import gi
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo
import math
import os
# TODO which version of cairo...?
import cairo
from io import BytesIO


class VOAPlotFilePrinter:
    #HEADER_HEIGHT = 10 * 72 / 25.4
    #HEADER_GAP = 3 * 72 / 25.4

    def __init__(self, canvas):
        self.operation = Gtk.PrintOperation()
        print_data = {'canvas': canvas,
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
        #base_name = os.path.splitext(os.path.basename(out_file_path))[0]
        uri = "file://{:s}/plot{:s}".format(dir, ext)
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

    def begin_print(self, operation, print_ctx, print_data):
        png_buffer = BytesIO()
        print_data['canvas'].print_figure(png_buffer, facecolor='white', edgecolor='white')
        print_data['png_buffer'] = png_buffer
        operation.set_n_pages(1)

    def draw_page(self, operation, print_ctx, page_num, print_data):
        cr = print_ctx.get_cairo_context()
        width = print_ctx.get_width()
        height = print_ctx.get_height()

        layout = print_ctx.create_pango_layout()

        print_data['png_buffer'].seek(0)
        plot_surface = cairo.ImageSurface.create_from_png(print_data['png_buffer'])
        # calculate proportional scaling
        # Thanks to
        # http://stackoverflow.com/questions/7145780/pycairo-how-to-resize-and-position-an-image
        plot_height = plot_surface.get_height()
        plot_width = plot_surface.get_width()
        width_ratio = float(width) / float(plot_width)
        height_ratio = float(height) / float(plot_height)
        scale_xy = min(height_ratio, width_ratio)
        cr.scale(scale_xy, scale_xy)
        cr.set_source_surface(plot_surface)
        cr.paint()


        PangoCairo.show_layout(cr, layout)
        layout = print_ctx.create_pango_layout()



    def end_print(self, operation, print_ctx, print_data):
        pass
        # delete the png here


def main(demoapp=None):
    app = VOAOutFilePrinter('/home/jwatson/itshfbc/run/voacapx.out')
    GLib.idle_add(app.run, demoapp)
    Gtk.main()

if __name__ == '__main__':
    main()
