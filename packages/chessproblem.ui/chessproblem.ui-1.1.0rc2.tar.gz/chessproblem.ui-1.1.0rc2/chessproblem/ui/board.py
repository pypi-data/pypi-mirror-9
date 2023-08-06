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
This module contains the following classes:
-   Board:
        displays a chess board
-   RowLegend:
        displays the row legend of a board (the numbers of the rows)
-   ColumnLegend:
        displays the column legend of a board (characters below the columns)
-   BoardSizeDialog: 
        used to change board size (for larger and smaller fairy boards)
-   PieceCountPanel:
        used to display the number of pieces within the statusbar
'''

from gi.repository import Gtk, Gdk, GObject
from gi.repository import Pango

import cairo

import logging
LOGGER = logging.getLogger('chessproblem.ui.board')

from chessproblem.model import PIECE_COLOR_WHITE, PIECE_COLOR_BLACK, PIECE_COLOR_NEUTRAL

from chessproblem.board_drawing import BoardDrawing, BOARD_BORDER_WIDTH
from .cairo_context_drawing_tool import CairoContextDrawingTool

class Board(Gtk.DrawingArea):
    '''
    A window used to display a chess board.
    '''
    def __init__(self, chessproblem, image_pixel_size):
        '''
        '''
        Gtk.DrawingArea.__init__(self)
        self.image_pixel_size = image_pixel_size
        self._listener = None
        self.connect('draw', self.on_expose_event)
        self.connect('button-release-event', self._on_button_release)
        # There seems to be a bug, so that we need to specify the button masks.
        self.set_events(Gdk.EventMask.EXPOSURE_MASK
                | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK )
        self.set_chessproblem(chessproblem)

    def set_chessproblem(self, chessproblem):
        '''
        Registers the given chessproblem and calculates the size of the visual chess board.
        '''
        self.chessproblem = chessproblem
        self.board_drawing = BoardDrawing(chessproblem, self.image_pixel_size)
        self.set_size_request(
                self.board_drawing.board_image_width(),
                self.board_drawing.board_image_height())
        self.queue_draw()

    def redraw(self):
        LOGGER.debug('Board.redraw()')
        self.queue_draw()

    def get_width(self):
        return self.board_drawing.board_image_width()

    def get_height(self):
        return self.board_drawing.board_image_height()

    def on_expose_event(self, area, cairo_context):
        '''
        Is registered to handle the expose event (which means redraw a specific region).
        In our case we just redraw the complete board.
        '''
        LOGGER.debug('Board.on_expose_event(...)')
        self.board_drawing.draw(CairoContextDrawingTool(cairo_context))

    def set_click_listener(self, listener):
        self._listener = listener

    def _on_button_release(self, widget, event, data=None):
        x = int(event.x)
        y = int(event.y)
        LOGGER.debug('_on_button_release(...) (x, y): (%d, %d)' % (x, y))
        if (x >= BOARD_BORDER_WIDTH) and (y >= BOARD_BORDER_WIDTH):
            row = self.chessproblem.board.rows - 1 - (y - BOARD_BORDER_WIDTH) // self.image_pixel_size
            column = (x - BOARD_BORDER_WIDTH) // self.image_pixel_size
            if self._listener != None:
                self._listener(row, column)


def legend_strategy_always(scrollbar, legend):
    '''
    A strategy for a legend, to make it visible always.
    '''
    legend.show()

def legend_strategy_never(scrollbar, legend):
    '''
    A strategy for a legend, to make it visible never.
    '''
    legend.hide()

def legend_strategy_automatic(scrollbar, legend):
    '''
    A strategy for a legend, to make it visible when the given scrollbar is visible.
    '''
    if scrollbar.get_property('visible'):
        legend.show()
    else:
        legend.hide()

def get_legend_strategy(name):
    if name == 'automatic':
        return legend_strategy_automatic
    elif name == 'never':
        return legend_strategy_never
    else:
        return legend_strategy_always

class RowLegend(Gtk.DrawingArea):
    '''
    Used to display the row-legend of a board.
    '''
    def __init__(self, rows, image_pixel_size):
        '''
        Creates the instances with the given initial number of rows.
        '''
        GObject.GObject.__init__(self)
        self.image_pixel_size = image_pixel_size
        self.connect('draw', self._on_expose_event)
        self._rows = -1
        self.set_rows(rows)

    def set_rows(self, rows):
        '''
        Change the display to the given number of rows.
        '''
        if rows != self._rows:
            self._rows = rows
            # We calculate the width depending on the width of the font
            layout = Pango.Layout(self.get_pango_context())
            layout.set_text('%d' % 8, 1)
            (width, height) = layout.get_pixel_size() 
            self._character_width = width
            self._width = 3 * self._character_width
            self._height = rows * self.image_pixel_size + 2 * BOARD_BORDER_WIDTH + 4
            self.set_size_request(self._width, self._height)
            self.queue_draw()

    def get_width(self):
        '''
        Returns the width of this RowLegend.
        '''
        return self._width

    def get_height(self):
        '''
        Returns the height of this RowLegend.
        '''
        return self._height

    def _on_expose_event(self, area, cairo_context):
        '''
        Is registered to be called when this RowLegend needs to be redrawn.
        '''
        self._draw_legend(cairo_context)

    def _draw_legend(self, cairo_context):
        '''
        Draws the row numbers for according to the current 'rows' value.
        '''
        cairo_context.set_source_rgb(0, 0, 0)
        for row in range(self._rows):
            cairo_context.move_to(2, 10 + self._height - ((row + 1) * self.image_pixel_size))
            cairo_context.show_text('%2d' % (row + 1))
            cairo_context.stroke()

        
class ColumnLegend(Gtk.DrawingArea):
    '''
    Used to display the column-legend of a board.
    '''
    def __init__(self, columns, image_pixel_size):
        '''
        Creates the instances with the given initial number of columns.
        '''
        Gtk.DrawingArea.__init__(self)
        self.image_pixel_size = image_pixel_size
        self.connect('draw', self._on_expose_event)
        self._columns = -1
        self.set_columns(columns)

    def set_columns(self, columns):
        '''
        Change the display to the given number of columns.
        '''
        if columns != self._columns:
            self._columns = columns
            # We calculate the width depending on the width of the font
            layout = Pango.Layout(self.get_pango_context())
            layout.set_text('J', 1)
            (width, height) = layout.get_pixel_size() 
            self._width = columns * self.image_pixel_size + 2 * BOARD_BORDER_WIDTH + 4
            self._yoffset = 2
            self._height = height + 4 * self._yoffset
            self._xoffset = (BOARD_BORDER_WIDTH + self.image_pixel_size - width) / 2
            self.set_size_request(self._width, self._height)
            self.queue_draw()

    def get_width(self):
        '''
        Returns the width of this ColumnLegend.
        '''
        return self._width

    def get_height(self):
        '''
        Returns the height of this ColumnLegend.
        '''
        return self._height

    def _on_expose_event(self, area, cairo_context):
        '''
        Is registered to be called when this ColumnLegend needs to be redrawn.
        '''
        self._draw_legend(cairo_context)

    def _draw_legend(self, cairo_context):
        '''
        Draws the column characters for according to the current 'columns' value.
        '''
        # layout = Pango.Layout(self.get_pango_context())
        cairo_context.set_source_rgb(0, 0, 0)
        for column in range(self._columns):
            cairo_context.move_to(self._xoffset + (column * self.image_pixel_size), self._yoffset + 10)
            cairo_context.show_text(chr(97 + column))
            cairo_context.stroke()

        
class BoardSizeDialog(Gtk.Dialog):
    '''
    This dialog is used to edit the size of the board.
    '''
    def __init__(self, rows, columns):
        Gtk.Dialog.__init__(self)
        self.set_title('edit board size')
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.rows = rows
        self.columns = columns
        self.table = Gtk.Grid()
        self.table.show()
        self.get_content_area().pack_start(self.table, True, True, 0)
        self.label_rows = Gtk.Label(label='rows')
        self.label_rows.show()
        self.table.attach(self.label_rows, 0, 0, 1, 1)
        self.adjustment_rows = Gtk.Adjustment(value = rows, lower=1, upper=26, step_incr=1)
        self.spin_rows = Gtk.SpinButton(adjustment=self.adjustment_rows)
        self.spin_rows.show()
        self.table.attach(self.spin_rows, 1, 0, 1, 1)
        self.label_columns = Gtk.Label(label='columns')
        self.label_columns.show()
        self.table.attach(self.label_columns, 0, 1, 1, 1)
        self.adjustment_columns = Gtk.Adjustment(value = columns, lower=1, upper=26, step_incr=1)
        self.spin_columns = Gtk.SpinButton(adjustment=self.adjustment_columns)
        self.spin_columns.show()
        self.table.attach(self.spin_columns, 1, 1, 1, 1)

    def get_rows(self):
        '''
        Returns the selected rows value.
        '''
        return int(self.adjustment_rows.get_value())

    def get_columns(self):
        '''
        Returns the selected columns value.
        '''
        return int(self.adjustment_columns.get_value())

class PieceCountPanel(Gtk.HBox):
    '''
    This panel us used to edit the piece counter to verify the board input.
    In addition to the verifying values (control counters), the instances stores the current counters.
    '''
    def __init__(self):
        Gtk.HBox.__init__(self)
        self.set_homogeneous(True)
        self.set_spacing(0)
        self.current_white = 0
        self.current_black = 0
        self.current_neutral = 0
        self._create_adjustment_and_pack_spinbutton('white')
        self._create_adjustment_and_pack_spinbutton('black')
        self._create_adjustment_and_pack_spinbutton('neutral')
        self._current_value_change_listeners = []
        LOGGER.debug('PieceCountPanel() ... created.')

    def _create_adjustment_and_pack_spinbutton(self, color):
        adjustment = Gtk.Adjustment()
        spinbutton = Gtk.SpinButton()
        setattr(self, 'adjustment_' + color, adjustment)
        setattr(self, 'spinbutton_' + color, spinbutton)
        adjustment.set_value(0)
        adjustment.set_lower(0)
        adjustment.set_upper(99)
        adjustment.set_step_increment(1)
        adjustment.set_page_increment(10)
        adjustment.set_page_size(0)
        adjustment.connect('value-changed', self._on_control_value_changed, color)
        spinbutton.set_adjustment(adjustment)
        spinbutton.show()
        self.pack_start(spinbutton, False, False, 2)

    def adjust_current_value(self, color, adjustment):
        value = getattr(self, 'current_' + color)
        value += adjustment
        setattr(self, 'current_' + color, value)
        self._on_current_value_changed(color)

    def set_current_values(self, white, black, neutral):
        '''
        Set the current piece count values.
        '''
        self.current_white = white
        self.current_black = black
        self.current_neutral = neutral
        self._on_current_values_changed()

    def set_control_counters(self, white, black, neutral):
        '''
        Display the given piece counter values inside the user interface elements.
        '''
        self.adjustment_white.set_value(white)
        self.adjustment_black.set_value(black)
        self.adjustment_neutral.set_value(neutral)

    def get_control_counters(self):
        '''
        Retrieve eht piece counters from the user interface elements.
        '''
        white = int(self.adjustment_white.get_value())
        black = int(self.adjustment_black.get_value())
        neutral = int(self.adjustment_neutral.get_value())
        return (white, black, neutral)

    def _get_control_counter(self, color):
        adjustment = getattr(self, 'adjustment_' + color)
        return int(adjustment.get_value())

    def _get_current_counter(self, color):
        return getattr(self, 'current_' + color)

    def _notify_listeners(self):
        for listener in self._current_value_change_listeners:
            listener(self.current_white, self.current_black, self.current_neutral)

    def _on_current_values_changed(self):
        '''
        Will be called, current piece counters change.
        '''
        for color in ['white', 'black', 'neutral']:
            self._on_current_value_changed(color, False)
        self._notify_listeners()

    def _on_control_value_changed(self, widget, color):
        self._adjust_color(color)

    def _on_current_value_changed(self, color, notify_listeners=True):
        '''
        '''
        self._adjust_color(color)
        if notify_listeners:
            self._notify_listeners()

    def add_current_listener(self, listener):
        self._current_value_change_listeners.append(listener)

    def piece_listener(self, oldpiece, newpiece):
        if oldpiece != None:
            if oldpiece.piece_color == PIECE_COLOR_WHITE:
                self.adjust_current_value('white', -1)
            elif oldpiece.piece_color == PIECE_COLOR_BLACK:
                self.adjust_current_value('black', -1)
            elif oldpiece.piece_color == PIECE_COLOR_NEUTRAL:
                self.adjust_current_value('neutral', -1)
        if newpiece != None:
            if newpiece.piece_color == PIECE_COLOR_WHITE:
                self.adjust_current_value('white', 1)
            elif newpiece.piece_color == PIECE_COLOR_BLACK:
                self.adjust_current_value('black', 1)
            elif newpiece.piece_color == PIECE_COLOR_NEUTRAL:
                self.adjust_current_value('neutral', 1)


    def _adjust_color(self, color):
        '''
        '''
        LOGGER.debug('PieceCountPanel._adjust_color(' + color + ')')
        spinbutton = getattr(self, 'spinbutton_' + color)
        if self._get_control_counter(color) == self._get_current_counter(color):
            spinbutton.override_color(Gtk.StateFlags.NORMAL, None)
        else:
            spinbutton.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 0, 0, 1))

