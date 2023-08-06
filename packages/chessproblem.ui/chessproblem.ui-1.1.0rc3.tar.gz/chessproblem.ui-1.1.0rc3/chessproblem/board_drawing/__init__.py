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

import logging
LOGGER = logging.getLogger('chessproblem.board_drawing')

EMPTY_BLACK_FIELD_INDEX = 144

BOARD_BORDER_WIDTH = 6

from chessproblem.image_files import image_offset

def _piece_image_offset(piece):
    '''
    Calculates the image offset for the given piece.
    '''
    return image_offset(piece.piece_type, piece.piece_color, piece.piece_rotation)


class BoardDrawing(object):
    '''
    Encapsulates the drawing of the chessboard using a 'DrawingTool'.
    '''

    def __init__(self, chessproblem, image_pixel_size, draw_outer_frame=False):
        LOGGER.debug('BoardDrawing.__init__(..., %d)' % image_pixel_size)
        self.chessproblem = chessproblem
        self.image_pixel_size = image_pixel_size
        self.draw_outer_frame = draw_outer_frame

    def board_image_width(self):
        result = self.chessproblem.board.columns * self.image_pixel_size + 2 * BOARD_BORDER_WIDTH
        LOGGER.debug('BoardDrawing.board_image_width() => %d' % result)
        return result

    def board_image_height(self):
        result = self.chessproblem.board.rows * self.image_pixel_size + 2 * BOARD_BORDER_WIDTH
        LOGGER.debug('BoardDrawing.board_image_height() => %d' % result)
        return result

    def draw(self, drawing_tool):
        '''
        Draw the registered chessproblem using the provided 'drawing_tool'
        '''
        LOGGER.debug('BoardDrawing.draw(...)')
        self._clear_board(drawing_tool)
        self._draw_border(drawing_tool)
        self._draw_fields(drawing_tool)
        self._draw_field_borders(drawing_tool)
        self._draw_grid(drawing_tool)
        self._draw_gridlines(drawing_tool)
        self._draw_fieldtext(drawing_tool)

    def _clear_board(self, drawing_tool):
        LOGGER.debug('BoardDrawing._clear_board(...)')
        drawing_tool.clear_rectangle(
                0, 0,
                self.board_image_width() - 1, self.board_image_height() - 1)

    def _draw_border(self, drawing_tool):
        '''
        Draws an outer and an inner boarder around the board.
        Parts or the complete inner boarder may be left out, when horizontalzylinder, verticalcylinder or noframe is used.
        '''
        LOGGER.debug('BoardDrawing._draw_border(...)')
        if self.draw_outer_frame:
            drawing_tool.draw_rectangle(
                    0, 0,
                    self.board_image_width() - 1, self.board_image_height() - 1)
        if not self.chessproblem.noframe:
            if not self.chessproblem.horizontalcylinder:
                drawing_tool.draw_line(
                        BOARD_BORDER_WIDTH - 1,
                        BOARD_BORDER_WIDTH - 1,
                        self.board_image_width() - BOARD_BORDER_WIDTH + 1,
                        BOARD_BORDER_WIDTH - 1)
                drawing_tool.draw_line(
                        BOARD_BORDER_WIDTH - 1,
                        self.board_image_height() - (BOARD_BORDER_WIDTH - 1),
                        self.board_image_width() - (BOARD_BORDER_WIDTH - 1),
                        self.board_image_height() - (BOARD_BORDER_WIDTH - 1))
            if not self.chessproblem.verticalcylinder:
                drawing_tool.draw_line(
                        BOARD_BORDER_WIDTH - 1,
                        BOARD_BORDER_WIDTH - 1,
                        BOARD_BORDER_WIDTH - 1,
                        self.board_image_height() - (BOARD_BORDER_WIDTH - 1))
                drawing_tool.draw_line(
                        self.board_image_width() - (BOARD_BORDER_WIDTH - 1),
                        BOARD_BORDER_WIDTH - 1,
                        self.board_image_width() - (BOARD_BORDER_WIDTH - 1),
                        self.board_image_height() - (BOARD_BORDER_WIDTH - 1))

    def _draw_fields(self, drawing_tool):
        LOGGER.debug('BoardDrawing._draw_fields(...)')
        for row in range(self.chessproblem.board.rows):
            for column in range(self.chessproblem.board.columns):
                self._draw_field(drawing_tool, row, column)

    def _draw_field(self, drawing_tool, row, column):
        LOGGER.debug('BoardDrawing._draw_field(..., %d, %d)' % (row, column))
        self._clear_field(drawing_tool, row, column)
        field = self.chessproblem.board.fields[row][column]
        if not field.is_nofield():
            piece = field.get_piece()
            if piece == None:
                self._draw_empty_field(drawing_tool, row, column)
            else:
                self._draw_piece(drawing_tool, piece, row, column)
        if field.has_frame():
            self._draw_field_frame(drawing_tool, row, column)

    def _draw_field_borders(self, drawing_tool):
        '''
        In case of an 'allwhite' problem, draws dotted lines between fields.
        '''
        LOGGER.debug('BoardDrawing._draw_borders(...)')
        if self.chessproblem.allwhite:
            for border in range(self.chessproblem.board.columns - 1):
                drawing_tool.draw_line(
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * (border+1)),
                        BOARD_BORDER_WIDTH,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * (border+1)),
                        self.board_image_height() - BOARD_BORDER_WIDTH,
                        True)
            for border in range(self.chessproblem.board.rows - 1):
                drawing_tool.draw_line(
                        BOARD_BORDER_WIDTH,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * (border+1)),
                        self.board_image_width() - BOARD_BORDER_WIDTH,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * (border+1)),
                        True)

    def _draw_grid(self, drawing_tool):
        '''
        Draws lines for a gridchess board.
        '''
        LOGGER.debug('BoardDrawing._draw_grid(...)')
        if self.chessproblem.gridchess:
            for gridline in range((self.chessproblem.board.columns - 1) // 2):
                drawing_tool.draw_line(
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * ((2 * gridline) + 2)),
                        BOARD_BORDER_WIDTH,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * ((2 * gridline) + 2)),
                        self.board_image_height() - BOARD_BORDER_WIDTH)
            for gridline in range((self.chessproblem.board.rows - 1) // 2):
                drawing_tool.draw_line(
                        BOARD_BORDER_WIDTH,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * ((2 * gridline) + 2)),
                        self.board_image_width() - BOARD_BORDER_WIDTH,
                        BOARD_BORDER_WIDTH + (self.image_pixel_size * ((2 * gridline) + 2)))

    def _draw_gridlines(self, drawing_tool):
        '''
        Draws the special gridlines into the board.
        '''
        LOGGER.debug('BoardDrawing._draw_gridlines(...)')
        for gridline in self.chessproblem.gridlines:
            line_x = BOARD_BORDER_WIDTH + (self.image_pixel_size * gridline.x)
            line_y = BOARD_BORDER_WIDTH + (self.image_pixel_size * (self.chessproblem.board.rows - gridline.y))
            line_length = self.image_pixel_size * gridline.length
            if gridline.orientation == 'h':
                drawing_tool.draw_line(line_x, line_y, line_x + line_length, line_y)
            elif gridline.orientation == 'v':
                drawing_tool.draw_line(line_x, line_y, line_x, line_y - line_length)

    def _draw_fieldtext(self, drawing_tool):
        '''
        Draws the fieldtexts into the board.
        '''
        LOGGER.debug('BoardDrawing._draw_fieldtext(...)')
        for fieldtext in self.chessproblem.fieldtext:
            x = BOARD_BORDER_WIDTH + (self.image_pixel_size * fieldtext.column)
            y = BOARD_BORDER_WIDTH + (self.image_pixel_size * (self.chessproblem.board.rows - fieldtext.row))
            drawing_tool.draw_text(self.image_pixel_size, fieldtext.text, x, y)

    def _clear_field(self, drawing_tool, row, column):
        LOGGER.debug('BoardDrawing._clear_field(..., %d, %d)' % (row, column))
        (x, y) = self._x_y_from_row_column(row, column)
        drawing_tool.clear_rectangle(
                x, y,
                self.image_pixel_size - 1, self.image_pixel_size - 1)

    def _draw_empty_field(self, drawing_tool, row, column):
        LOGGER.debug('BoardDrawing._draw_empty_field(..., %d, %d)' % (row, column))
        if self._is_black_field(row, column):
            self._draw_chess_image(drawing_tool, 144, row, column)

    def _draw_piece(self, drawing_tool, piece, row, column):
        LOGGER.debug('BoardDrawing._draw_piece(..., %r, %d, %d)' % (piece, row, column))
        if self._is_black_field(row, column):
            piece_image_offset = _piece_image_offset(piece) + 18
        else:
            piece_image_offset = _piece_image_offset(piece)
        self._draw_chess_image(drawing_tool, piece_image_offset, row, column)

    def _draw_chess_image(self, drawing_tool, image_index, row, column):
        LOGGER.debug('BoardDrawing._draw_chess_image(..., %d, %d, %d)' % (image_index, row, column))
        (x, y) = self._x_y_from_row_column(row, column)
        drawing_tool.draw_chessimage(self.image_pixel_size, image_index, x, y)

    def _draw_field_frame(self, drawing_tool, row, column):
        LOGGER.debug('BoardDrawing._draw_field_frame(..., %d, %d)' % (row, column))
        (x, y) = self._x_y_from_row_column(row, column)
        drawing_tool.draw_rectangle(x, y, self.image_pixel_size, self.image_pixel_size)

    def _x_y_from_row_column(self, row, column):
        x = column * self.image_pixel_size
        y = (self.chessproblem.board.rows - 1 - row) * self.image_pixel_size
        result = (x + BOARD_BORDER_WIDTH, y + BOARD_BORDER_WIDTH)
        LOGGER.debug('BoardDrawing._x_y_from_row_column(%d, %d) => %r' % (row, column, result))
        return result

    def _is_black_field(self, row, column):
        if self.chessproblem.allwhite:
            result = False
        if self.chessproblem.switchcolors:
            result = (row + column) % 2 == 1
        else:
            result = (row + column) % 2 == 0
        LOGGER.debug('BoardDrawing._is_black_field(%d, %d) => %r' % (row, column, result))
        return result

