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

import unittest

import logging

filehandler = logging.FileHandler('parse_ffen_test.log')

ffen_logger = logging.getLogger('chessproblem.tools.ffen')
ffen_logger.setLevel(logging.DEBUG)
ffen_logger.addHandler(filehandler)

from chessproblem.tools.ffen import parse_ffen, ParseFFENException

from chessproblem.model import (PIECE_COLOR_WHITE, PIECE_COLOR_BLACK,
        PIECE_COLOR_NEUTRAL)
from chessproblem.model import (PIECE_TYPE_PAWN, PIECE_TYPE_KNIGHT,
        PIECE_TYPE_BISHOP, PIECE_TYPE_ROOK, PIECE_TYPE_QUEEN, PIECE_TYPE_KING,
        PIECE_TYPE_EQUIHOPPER, PIECE_TYPE_CIRCLE)
from chessproblem.model import (PIECE_ROTATION_NORMAL, PIECE_ROTATION_LEFT,
        PIECE_ROTATION_RIGHT, PIECE_ROTATION_UPSIDEDOWN, PIECE_ROTATION_COUNT)

class ParseFFENTest(unittest.TestCase):

    def test_parse_empty_8x8_board(self):
        board = parse_ffen('8/8/8/8/8/8/8/8')
        self.assertIsNotNone(board)
        self.assertEqual(8, board.rows)
        self.assertEqual(8, board.columns)

    def test_parse_empty_7x4_board(self):
        board = parse_ffen('7/7/7/7')
        self.assertIsNotNone(board)
        self.assertEqual(4, board.rows)
        self.assertEqual(7, board.columns)

    def test_parse_nonunique_columns(self):
        try:
            board = parse_ffen('7/7/5/7')
            self.assertTrue(False)
        except ParseFFENException as e:
            pass

    def test_parse_PAS(self):
        board = parse_ffen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        self.assertIsNotNone(board)
        self.assertEqual(8, board.rows)
        self.assertEqual(8, board.columns)
        for row in range(8):
            for column in range(8):
                piece = board.fields[row][column].get_piece()
                if row in [2, 3, 4, 5]:
                    self.assertIsNone(piece)
                else:
                    self.assertIsNotNone(piece)
                    if row in [1, 6]:
                        self.assertEqual(PIECE_TYPE_PAWN, piece.piece_type)
                    if row in [0, 1]:
                        self.assertEqual(PIECE_COLOR_WHITE, piece.piece_color)
                    if row in [6, 7]:
                        self.assertEqual(PIECE_COLOR_BLACK, piece.piece_color)



if __name__ == '__main__':
    unittest.main()

