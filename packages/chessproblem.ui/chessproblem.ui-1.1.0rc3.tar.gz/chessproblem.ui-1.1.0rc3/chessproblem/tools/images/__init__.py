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
This module contains code to generate images from chessproblems.
'''

import logging
LOGGER = logging.getLogger('chessproblem.tools.images')

from chessproblem.model import Chessproblem

from chessproblem.board_drawing import BOARD_BORDER_WIDTH, BoardDrawing

from chessproblem.image_files import get_png_filename

from PIL import Image, ImageDraw, ImageFont

class PillowDrawingTool(object):
    '''
    A 'drawing_tool' implementation for use in class BoardDrawing, which draws
    the board to an PIL image, which can be saved as PNG, JPEG, etc.
    '''

    def __init__(self, width, height):
        LOGGER.debug('PillowDrawingTool.__init__(..)')
        self.image = Image.new('1', (width, height))
        self.draw = ImageDraw.Draw(self.image)

    def clear_rectangle(self, x, y, width, height):
        LOGGER.debug('PillowDrawingTool.clear_rectangle(%d, %d, %d, %d)' % (x, y, width, height))
        self.draw.rectangle([x, y, x + width, y + height], fill=1)

    def draw_rectangle(self, x, y, width, height):
        LOGGER.debug('PillowDrawingTool.draw_rectangle(%d, %d, %d, %d)' % (x, y, width, height))
        self.draw.rectangle([x, y, x + width, y + height], outline=0)

    def draw_line(self, x1, y1, x2, y2, dotted=False):
        LOGGER.debug('PillowDrawingTool.draw_line(%d, %d, %d, %d, %r)' % (x1, y1, x2, y2, dotted))
        if dotted:
            pass
        else:
            self.draw.line([x1, y1, x2, y2], fill=0)

    def draw_chessimage(self, image_pixel_size, image_index, x, y):
        LOGGER.debug('PillowDrawingTool.draw_chessimage(%d, %d, %d, %d)' % (image_pixel_size, image_index, x, y))
        png_filename = get_png_filename(image_index, image_pixel_size)
        piece_image = Image.open(png_filename)
        (width, height) = piece_image.size
        piece_bitmap = piece_image.tobitmap()
        if width < image_pixel_size:
            x_offset = (image_pixel_size - width) // 2
            x = x + x_offset
        if height < image_pixel_size:
            y_offset = (image_pixel_size - height) // 2
            y = y + y_offset
        # self.draw.rectangle([x, y, x + width, y + height], fill=0)
        # self.draw.bitmap((x, y), piece_image, fill=1)
        self.image.paste(piece_image, (x, y))

    def draw_text(self, image_pixel_size, text, x, y):
        LOGGER.debug('PillowDrawingTool.draw_text(%d, %s, %d, %d)' % (image_pixel_size, text, x, y))
        font = ImageFont.truetype(font='arial.ttf', size=image_pixel_size // 2)
        width, height = self.draw.textsize(text, font=font)
        x_offset = (image_pixel_size - width) // 2
        y_offset = (height // 2) - image_pixel_size
        LOGGER.debug('PillowDrawingTool.draw_text(...) text width/height: %d/%d - x_offset/y_offset: %d/%d' % (width, height, x_offset, y_offset))
        self.draw.text((x + x_offset, y + y_offset), text, fill=0, font=font)

    def get_image(self):
        LOGGER.debug('PillowDrawingTool.get_image()')
        return self.image

def create_image(chessproblem, image_pixel_size):
    width = 2 * BOARD_BORDER_WIDTH + image_pixel_size * chessproblem.board.columns
    height = 2 * BOARD_BORDER_WIDTH + image_pixel_size * chessproblem.board.rows
    drawing_tool = PillowDrawingTool(width, height)
    board_drawing = BoardDrawing(chessproblem, image_pixel_size)
    board_drawing.draw(drawing_tool)
    return drawing_tool.get_image()

from chessproblem.config import create_config
from chessproblem.ui.help import CPE_BOARD_TEX
from chessproblem.io import ChessProblemLatexParser
from chessproblem.model.memory_db import create_memory_db

def main():
    cpe_config = create_config()
    memory_db_service = create_memory_db(cpe_config.config_dir)
    parser = ChessProblemLatexParser(cpe_config, memory_db_service)
    document = parser.parse_latex_str(CPE_BOARD_TEX)
    chessproblem = document.get_problem(0)
    image = create_image(chessproblem, 40)
    image.save('empty_board.png')

if __name__ == '__main__':
    main()

