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

from chessproblem.model import Board, Field, Piece

import logging

LOGGER = logging.getLogger('chessproblem.tools.ffen')

class FFENExecption(Exception):
    pass

def generate_ffen(chessproblem, ignore_unsupported=True):
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


class ParseFFENException(Exception):
    pass

_MODEL_PIECETYPES = {
        'p': PIECE_TYPE_PAWN,
        'n': PIECE_TYPE_KNIGHT,
        'b': PIECE_TYPE_BISHOP,
        'r': PIECE_TYPE_ROOK,
        'q': PIECE_TYPE_QUEEN,
        'k': PIECE_TYPE_KING }

_MODEL_ROTATIONS = [ PIECE_ROTATION_NORMAL, PIECE_ROTATION_RIGHT,
        PIECE_ROTATION_UPSIDEDOWN, PIECE_ROTATION_LEFT ]

def _model_piecetype(ffen_piecetype):
    search = ffen_piecetype.lower()
    return _MODEL_PIECETYPES[search]

def _new_piece(piece_color, piece_type, piece_rotation):
    piece = Piece(piece_color, piece_type, piece_rotation)
    result = Field()
    result.set_piece(piece)
    return result

def parse_ffen(ffen):
    LOGGER.debug('parse_ffen(%s)' % ffen)
    row = []
    rows = [ row ]
    index = 0
    piece_color = None
    piece_rotation = PIECE_ROTATION_NORMAL
    while index < len(ffen):
        c = ffen[index]
        if c == '/':
            LOGGER.debug('parse_ffen(...) start new row')
            row = []
            rows.append(row)
        elif c in '123456789':
            LOGGER.debug('parse_ffen(...) skip %d fields' % int(c))
            for empty_field in range(int(c)):
                row.append(Field())
        elif c == '-':
            piece_color = PIECE_COLOR_NEUTRAL
        elif c == '*':
            # determine rotation
            index += 1
            c = ffen[index]
            if c in '123':
                piece_rotation = _MODEL_ROTATIONS[int(c)]
            else:
                raise ParseFFENException('Invalid rotation %s at index %d' % (c, index + 1))
        elif c in 'pnbrqk':
            if piece_color == None:
                piece_color = PIECE_COLOR_BLACK
            row.append(_new_piece(piece_color, _model_piecetype(c), piece_rotation))
            piece_color = None
            piece_rotation = PIECE_ROTATION_NORMAL
        elif c in 'PNBRQK':
            if piece_color == None:
                piece_color = PIECE_COLOR_WHITE
            row.append(_new_piece(piece_color, _model_piecetype(c), piece_rotation))
            piece_color = None
            piece_rotation = PIECE_ROTATION_NORMAL
        else:
            raise ParseFFENException('Unknown code %s at index %d' % (c, index))
        index += 1
    result = Board()
    result.columns = None
    result.rows = len(rows)
    result.fields = []
    for row_index in range(len(rows)):
        row_fields = rows[result.rows - row_index - 1]
        if result.columns != None:
            if result.columns != len(row_fields):
                raise ParseFFENException('row %d has different number of columns %d than before %d' % (row_index, len(row_fields), result.columns))
        else:
            result.columns = len(row_fields)
        result.fields.append([field for field in row_fields])

    return result


