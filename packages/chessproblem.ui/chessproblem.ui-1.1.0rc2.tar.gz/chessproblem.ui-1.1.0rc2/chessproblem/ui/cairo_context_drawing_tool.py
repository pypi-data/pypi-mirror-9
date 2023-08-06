# Copyright 2012 Stefan Hoening
# 
# This file is part of the "Chess-Problem-Editor" software.
# 
# Chess-Problem-Editor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Chess-Problem-Editor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Diese Datei ist Teil der Software "Chess-Problem-Editor".
# 
# Chess-Problem-Editor ist Freie Software: Sie koennen es unter den Bedingungen
# der GNU General Public License, wie von der Free Software Foundation,
# Version 3 der Lizenz oder (nach Ihrer Option) jeder spaeteren
# veroeffentlichten Version, weiterverbreiten und/oder modifizieren.
# 
# Chess-Problem-Editor wird in der Hoffnung, dass es nuetzlich sein wird, aber
# OHNE JEDE GEWAEHRLEISTUNG, bereitgestellt; sogar ohne die implizite
# Gewaehrleistung der MARKTFAEHIGKEIT oder EIGNUNG FUER EINEN BESTIMMTEN ZWECK.
# Siehe die GNU General Public License fuer weitere Details.
# 
# Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
# Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.

'''
This module implements the a concrete 'DrawingTool' implementation to draw
a board using a cairo_context (gtk)
'''

import logging
LOGGER = logging.getLogger('chessproblem.ui.cairo_context_drawing_tool')

from chessproblem.image_files import create_chessimage_surface

class CairoContextDrawingTool(object):
    '''
    A 'drawing_tool' implementation for use in class BoardDrawing, which draws
    the board to the cairo_context registered in constructor.
    '''

    def __init__(self, cairo_context):
        LOGGER.debug('CairoContextDrawingTool.__init__(..) %r' % type(cairo_context))
        self.cairo_context = cairo_context

    def clear_rectangle(self, x, y, width, height):
        LOGGER.debug('CairoContextDrawingTool.clear_rectangle(%d, %d, %d, %d)' % (x, y, width, height))
        self.cairo_context.set_dash([])
        self.cairo_context.set_source_rgb(1.0, 1.0, 1.0)
        self.cairo_context.rectangle(x, y, width, height)
        self.cairo_context.fill()

    def draw_rectangle(self, x, y, width, height):
        LOGGER.debug('CairoContextDrawingTool.draw_rectangle(%d, %d, %d, %d)' % (x, y, width, height))
        self.cairo_context.set_dash([])
        self.cairo_context.set_source_rgb(0.0, 0.0, 0.0)
        self.cairo_context.rectangle(x, y, width, height)
        self.cairo_context.stroke()

    def draw_line(self, x1, y1, x2, y2, dotted=False):
        LOGGER.debug('CairoContextDrawingTool.draw_line(%d, %d, %d, %d, %r)' % (x1, y1, x2, y2, dotted))
        self.cairo_context.set_source_rgb(0, 0, 0)
        if dotted:
            self.cairo_context.set_dash([2], 1)
        else:
            self.cairo_context.set_dash([])
        self.cairo_context.move_to(x1, y1)
        self.cairo_context.line_to(x2, y2)
        self.cairo_context.stroke()

    def draw_chessimage(self, image_pixel_size, image_index, x, y):
        LOGGER.debug('CairoContextDrawingTool.draw_chessimage(%d, %d, %d, %d)' % (image_pixel_size, image_index, x, y))
        surface = create_chessimage_surface(image_index, image_pixel_size)
        if surface.get_width() < image_pixel_size:
            x = x + ((image_pixel_size - surface.get_width()) / 2)
        if surface.get_height() < image_pixel_size:
            y = y + ((image_pixel_size - surface.get_height()) / 2)
        self.cairo_context.set_source_rgb(0, 0, 0)
        self.cairo_context.set_source_surface(surface, x, y)
        self.cairo_context.rectangle(x, y, image_pixel_size, image_pixel_size)
        self.cairo_context.fill()

    def draw_text(self, image_pixel_size, text, x, y):
        LOGGER.debug('CairoContextDrawingTool.draw_text(%s, %d, %d)' % (text, x, y))
        self.cairo_context.set_source_rgb(0, 0, 0)
        self.cairo_context.set_font_size(image_pixel_size / 2)
        text_extent = self.cairo_context.text_extents(text)
        width = text_extent[2]
        height = text_extent[3]
        x_offset = (image_pixel_size - width) // 2
        y_offset = (height - image_pixel_size) // 2
        self.cairo_context.move_to(x + x_offset, y + y_offset)
        self.cairo_context.show_text(text)

