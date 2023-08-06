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
This module contains testcases for the "Fairy FEN" creation.
'''

from chessproblem.model import (Chessproblem, ChessproblemDocument, Piece,
        PIECE_COLOR_WHITE, PIECE_COLOR_BLACK, PIECE_COLOR_NEUTRAL,
        PIECE_TYPE_PAWN, PIECE_TYPE_KNIGHT, PIECE_TYPE_BISHOP, PIECE_TYPE_ROOK,
        PIECE_TYPE_QUEEN, PIECE_TYPE_KING, PIECE_TYPE_CIRCLE)

from chessproblem.model import PIECE_ROTATION_NORMAL, PIECE_ROTATION_LEFT, PIECE_ROTATION_RIGHT, PIECE_ROTATION_UPSIDEDOWN, PIECE_ROTATION_COUNT

from chessproblem.config import create_config

from chessproblem.io import ChessProblemLatexParser

from sqlalchemy.orm import clear_mappers

from chessproblem.model.memory_db import create_memory_db

import unittest

import logging

LOGGER = logging.getLogger('chessproblem.tools.fen')
LOGGER.setLevel(logging.DEBUG)
filehandler = logging.FileHandler('create_ffen.log')
LOGGER.addHandler(filehandler)

from chessproblem.tools.ffen import generate_ffen, _ffen_piece, _ffen_piece_name, _ffen_piece_rotation

class FFENTest(unittest.TestCase):
    def setUp(self):
        self.empty_problem = Chessproblem()
        self.cpe_config = create_config()
        clear_mappers()
        self.db_service = create_memory_db(self.cpe_config.config_dir)
        self.parser = ChessProblemLatexParser(self.cpe_config, self.db_service)

    def test_empty_normal_board(self):
        self.assertEqual('8/8/8/8/8/8/8/8', generate_ffen(self.empty_problem))

    def test_empty_3x4_board(self):
        self.assertEqual('3/3/3/3', generate_ffen(self._create_problem_from_string(
            '\\begin{diagram}[3x4]\\end{diagram}')))

    def test_extended_party_starting_position_normal(self):
        self.assertEqual('rnbqkbnr/pppppppp/8/-p-p-p-p-p-p-p-p/-r-n-b-q-k-b-n-r/8/PPPPPPPP/RNBQKBNR',
                generate_ffen(self._create_problem_from_string('''\\begin{diagram}\\pieces{wKe1, wDd1, wTa1h1, wLc1f1, wSb1g1, wBa2b2c2d2e2f2g2h2, nKe4, nDd4, nTa4h4, nLc4f4, nSb4g4, nBa5b5c5d5e5f5g5h5, sKe8, sDd8, sTa8h8, sLc8f8, sSb8g8, sBa7b7c7d7e7f7g7h7}\\end{diagram}''')))

    def test_extended_party_starting_position_left(self):
        self.maxDiff = None
        self.assertEqual('*3r*3n*3b*3q*3k*3b*3n*3r/*3p*3p*3p*3p*3p*3p*3p*3p/8/-*3p-*3p-*3p-*3p-*3p-*3p-*3p-*3p/-*3r-*3n-*3b-*3q-*3k-*3b-*3n-*3r/8/*3P*3P*3P*3P*3P*3P*3P*3P/*3R*3N*3B*3Q*3K*3B*3N*3R',
                generate_ffen(self._create_problem_from_string('''\\begin{diagram}\\pieces{wKLe1, wDLd1, wTLa1h1, wLLc1f1, wSLb1g1, wBLa2b2c2d2e2f2g2h2, nKLe4, nDLd4, nTLa4h4, nLLc4f4, nSLb4g4, nBLa5b5c5d5e5f5g5h5, sKLe8, sDLd8, sTLa8h8, sLLc8f8, sSLb8g8, sBLa7b7c7d7e7f7g7h7}\\end{diagram}''')))


    def test_extended_party_starting_position_upsidedown(self):
        self.maxDiff = None
        self.assertEqual('*2r*2n*2b*2q*2k*2b*2n*2r/*2p*2p*2p*2p*2p*2p*2p*2p/8/-*2p-*2p-*2p-*2p-*2p-*2p-*2p-*2p/-*2r-*2n-*2b-*2q-*2k-*2b-*2n-*2r/8/*2P*2P*2P*2P*2P*2P*2P*2P/*2R*2N*2B*2Q*2K*2B*2N*2R',
                generate_ffen(self._create_problem_from_string('''\\begin{diagram}\\pieces{wKUe1, wDUd1, wTUa1h1, wLUc1f1, wSUb1g1, wBUa2b2c2d2e2f2g2h2, nKUe4, nDUd4, nTUa4h4, nLUc4f4, nSUb4g4, nBUa5b5c5d5e5f5g5h5, sKUe8, sDUd8, sTUa8h8, sLUc8f8, sSUb8g8, sBUa7b7c7d7e7f7g7h7}\\end{diagram}''')))


    def test_extended_party_starting_position_right(self):
        self.maxDiff = None
        self.assertEqual('*1r*1n*1b*1q*1k*1b*1n*1r/*1p*1p*1p*1p*1p*1p*1p*1p/8/-*1p-*1p-*1p-*1p-*1p-*1p-*1p-*1p/-*1r-*1n-*1b-*1q-*1k-*1b-*1n-*1r/8/*1P*1P*1P*1P*1P*1P*1P*1P/*1R*1N*1B*1Q*1K*1B*1N*1R',
                generate_ffen(self._create_problem_from_string('''\\begin{diagram}\\pieces{wKRe1, wDRd1, wTRa1h1, wLRc1f1, wSRb1g1, wBRa2b2c2d2e2f2g2h2, nKRe4, nDRd4, nTRa4h4, nLRc4f4, nSRb4g4, nBRa5b5c5d5e5f5g5h5, sKRe8, sDRd8, sTRa8h8, sLRc8f8, sSRb8g8, sBRa7b7c7d7e7f7g7h7}\\end{diagram}''')))
    def test_ffen_piece_name(self):
        # white
        self.assertEqual('K', _ffen_piece_name(PIECE_COLOR_WHITE, PIECE_TYPE_KING))
        self.assertEqual('Q', _ffen_piece_name(PIECE_COLOR_WHITE, PIECE_TYPE_QUEEN))
        self.assertEqual('R', _ffen_piece_name(PIECE_COLOR_WHITE, PIECE_TYPE_ROOK))
        self.assertEqual('B', _ffen_piece_name(PIECE_COLOR_WHITE, PIECE_TYPE_BISHOP))
        self.assertEqual('N', _ffen_piece_name(PIECE_COLOR_WHITE, PIECE_TYPE_KNIGHT))
        self.assertEqual('P', _ffen_piece_name(PIECE_COLOR_WHITE, PIECE_TYPE_PAWN))
        self.assertEqual('C', _ffen_piece_name(PIECE_COLOR_WHITE, PIECE_TYPE_CIRCLE))
        # black
        self.assertEqual('k', _ffen_piece_name(PIECE_COLOR_BLACK, PIECE_TYPE_KING))
        self.assertEqual('q', _ffen_piece_name(PIECE_COLOR_BLACK, PIECE_TYPE_QUEEN))
        self.assertEqual('r', _ffen_piece_name(PIECE_COLOR_BLACK, PIECE_TYPE_ROOK))
        self.assertEqual('b', _ffen_piece_name(PIECE_COLOR_BLACK, PIECE_TYPE_BISHOP))
        self.assertEqual('n', _ffen_piece_name(PIECE_COLOR_BLACK, PIECE_TYPE_KNIGHT))
        self.assertEqual('p', _ffen_piece_name(PIECE_COLOR_BLACK, PIECE_TYPE_PAWN))
        self.assertEqual('c', _ffen_piece_name(PIECE_COLOR_BLACK, PIECE_TYPE_CIRCLE))
        # neutral
        self.assertEqual('k', _ffen_piece_name(PIECE_COLOR_NEUTRAL, PIECE_TYPE_KING))
        self.assertEqual('q', _ffen_piece_name(PIECE_COLOR_NEUTRAL, PIECE_TYPE_QUEEN))
        self.assertEqual('r', _ffen_piece_name(PIECE_COLOR_NEUTRAL, PIECE_TYPE_ROOK))
        self.assertEqual('b', _ffen_piece_name(PIECE_COLOR_NEUTRAL, PIECE_TYPE_BISHOP))
        self.assertEqual('n', _ffen_piece_name(PIECE_COLOR_NEUTRAL, PIECE_TYPE_KNIGHT))
        self.assertEqual('p', _ffen_piece_name(PIECE_COLOR_NEUTRAL, PIECE_TYPE_PAWN))
        self.assertEqual('c', _ffen_piece_name(PIECE_COLOR_NEUTRAL, PIECE_TYPE_CIRCLE))

    def test_ffen_piece_rotation(self):
        self.assertEqual('', _ffen_piece_rotation(PIECE_ROTATION_NORMAL))
        self.assertEqual('*3', _ffen_piece_rotation(PIECE_ROTATION_LEFT))
        self.assertEqual('*2', _ffen_piece_rotation(PIECE_ROTATION_UPSIDEDOWN))
        self.assertEqual('*1', _ffen_piece_rotation(PIECE_ROTATION_RIGHT))

    def _create_problem_from_string(self, string):
        document = self.parser.parse_latex_str(string)
        return document.get_problem(0)

if __name__ == '__main__':
    unittest.main()

