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
This module contains code to create "Fairy FEN" notation from a problem.
'''


import io

from chessproblem.model import Chessproblem, ChessproblemDocument
from chessproblem.model import PIECE_COLOR_WHITE, PIECE_COLOR_BLACK, PIECE_COLOR_NEUTRAL
from chessproblem.model import (PIECE_TYPE_PAWN, PIECE_TYPE_KNIGHT,
        PIECE_TYPE_BISHOP, PIECE_TYPE_ROOK, PIECE_TYPE_QUEEN, PIECE_TYPE_KING,
        PIECE_TYPE_EQUIHOPPER, PIECE_TYPE_CIRCLE)
from chessproblem.model import PIECE_ROTATION_NORMAL, PIECE_ROTATION_LEFT, PIECE_ROTATION_RIGHT, PIECE_ROTATION_UPSIDEDOWN, PIECE_ROTATION_COUNT


import logging

LOGGER = logging.getLogger('chessproblem.tools.ffen')

class FFENExecption(Exception):
    pass

def ffen(chessproblem, ignore_unsupported=True):
    '''
    converts the given chessproblem to "Fairy FEN"
    '''
    result = io.StringIO()

    board = chessproblem.board
    for row in reversed(range(board.rows)):
        if row < board.rows - 1:
            result.write('/')
        empty_count = 0
        last_piece = True
        column_fields = board.fields[row]
        for field in column_fields:
            if not ignore_unsupported:
                if field.has_frame():
                    raise FFENException('fieldframe unsupported in FFEN')
                if field.is_nofield():
                    raise FFENExcetpion('nofield unsupported in FFEN')
            piece = field.get_piece()
            if piece != None:
                if empty_count > 0:
                    result.write('%d' % empty_count)
                    empty_count = 0
                result.write(_ffen_piece(piece))
            else:
                empty_count = empty_count + 1
        if empty_count > 0:
            result.write('%d' % empty_count)
            empty_count = 0

    return result.getvalue()

_FFEN_PIECE_NAMES = [
        [ 'P', 'N', 'B', 'R', 'Q', 'K', '', 'C' ],
        [ 'p', 'n', 'b', 'r', 'q', 'k', '', 'c' ]]

def _ffen_piece_name(piece_color, piece_type, piece_rotation=PIECE_ROTATION_NORMAL):
    if piece_type != PIECE_TYPE_EQUIHOPPER:
        if piece_color == PIECE_COLOR_WHITE:
            piece_names = _FFEN_PIECE_NAMES[0]
        else:
            piece_names = _FFEN_PIECE_NAMES[1]
        return piece_names[piece_type]
    else:
        raise FFENExecption('No FFEN symbol for equihopper.')

_FFEN_PIECE_ROTATION = [ 3, 1, 2 ]

def _ffen_piece_rotation(piece_rotation):
    if piece_rotation > 0:
        return '*%d' % _FFEN_PIECE_ROTATION[piece_rotation - 1]
    else:
        return ''

def _ffen_color_prefix(piece_color):
    if piece_color == PIECE_COLOR_NEUTRAL:
        return '-'
    else:
        return ''

def _ffen_piece(piece):
    '''
    calculates the FFEN notation for the given piece
    '''
    result = io.StringIO()

    result.write(_ffen_color_prefix(piece.piece_color))
    result.write(_ffen_piece_rotation(piece.piece_rotation))
    result.write(_ffen_piece_name(piece.piece_color, piece.piece_type))

    return result.getvalue()
