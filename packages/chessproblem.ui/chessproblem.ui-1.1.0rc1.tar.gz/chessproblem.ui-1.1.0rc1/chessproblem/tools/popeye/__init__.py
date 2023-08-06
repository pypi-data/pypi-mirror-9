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
This module contains code to create popeye input from a given problem.
'''

import io

from chessproblem.model import Chessproblem, ChessproblemDocument
from chessproblem.model import PIECE_COLOR_WHITE, PIECE_COLOR_BLACK, PIECE_COLOR_NEUTRAL
from chessproblem.model import PIECE_ROTATION_NORMAL, PIECE_ROTATION_LEFT, PIECE_ROTATION_RIGHT, PIECE_ROTATION_UPSIDEDOWN, PIECE_ROTATION_COUNT

from chessproblem.io import PIECE_TYPE_OUTPUT_ORDER, PIECE_CHARACTERS, COLUMN_CHARACTERS, PIECE_ROTATIONS

import logging

LOGGER = logging.getLogger('chessproblem.tools.popeye')

class PopeyeException(Exception):
    pass

class Popeye(object):
    '''
    This class provides the generation of an input stream of a given chessproblem.
    '''
    def __init__(self, memory_db_service):
        self._memory_db_service = memory_db_service

    def create_popeye_input(self, chessproblems):
        '''
        Creates popeye input for the given chessproblems.
        '''
        with io.StringIO() as output:
            output.write('anfangproblem\n\n')

            if isinstance(chessproblems, Chessproblem):
                output.write(self.create_single_problem_input(chessproblems))
            elif isinstance(chessproblems, ChessproblemDocument):
                for i in range(chessproblems.get_problem_count()):
                    cp = chessproblems.get_problem(i)
                    try:
                        popeye_input = self.create_single_problem_input(cp)
                        if i > 0:
                            output.write('\nweiteresproblem\n\n')
                        output.write(popeye_input)
                    except PopeyeException as pe:
                        output.write('\nbemerkung %s %s\n\n' % ('ERROR', str(pe)))

            output.write('\nendeproblem\n')

            return output.getvalue()

    def create_single_problem_input(self, chessproblem):
        if chessproblem.board.rows == 8 and chessproblem.board.columns == 8:
            with io.StringIO() as output:
                self._write_author(chessproblem.authors, output)
                output.write('forderung ')
                if chessproblem.stipulation != None:
                    output.write(self._convert_stipulation(chessproblem.stipulation))
                output.write('\n')
                self._write_conditions(chessproblem.condition, output)
                output.write('\n')
                self._write_board(chessproblem, output)
                return output.getvalue()
        else:
            raise PopeyeException('board size not supported')

    def _write_author(self, authors, output):
        for author in authors:
            output.write('autor %s %s\n' % (author.firstname, author.lastname))

    def _convert_stipulation(self, stipulation):
        '''
        Some special latex stuff should be replaced for a valid popeye stipulation.
        '''
        return stipulation.replace('\\#', '#')

    def _write_conditions(self, conditions, output):
        non_popeye_conditions = []
        popeye_conditions = []
        if conditions != None:
            for condition in conditions:
                popeye_name = condition.get_popeye_name()
                if popeye_name:
                    popeye_conditions.append(popeye_name)
                else:
                    non_popeye_conditions.append(condition.get_name())
        if len(popeye_conditions) > 0:
            output.write('bedingung')
            for condition in popeye_conditions:
                output.write(' %s' % condition)
            output.write('\n\n')
        for condition in non_popeye_conditions:
            output.write('bemerkung   non popeye condition %s\n' % condition)


    def _write_board(self, chessproblem, output):
        '''
        Write the position to the output.
        '''
        (white, black, neutral) = chessproblem.board.get_pieces_count()
        if (white > 0) or (black > 0) or (neutral > 0):
            output.write('steine\n')
            if white > 0:
                output.write('weiss  ')
                self._write_pieces(chessproblem, output, PIECE_COLOR_WHITE)
                output.write('\n')
            if black > 0:
                output.write('schwarz')
                self._write_pieces(chessproblem, output, PIECE_COLOR_BLACK)
                output.write('\n')
            if neutral > 0:
                output.write('neutral')
                self._write_pieces(chessproblem, output, PIECE_COLOR_NEUTRAL)
                output.write('\n')


    def _write_pieces(self, chessproblem, output, piece_color):
        for piece_rotation in range(PIECE_ROTATION_COUNT):
            for piece_type in PIECE_TYPE_OUTPUT_ORDER:
                piece_name = None
                for row in range(chessproblem.board.rows):
                    for column in range(chessproblem.board.columns):
                        piece = chessproblem.board.fields[row][column].get_piece()
                        if (piece != None
                            and piece.piece_color == piece_color
                            and piece.piece_rotation == piece_rotation
                            and piece.piece_type == piece_type):
                            if piece_name == None:
                                piece_name = self._get_piece_name(chessproblem, piece_type, piece_rotation)
                                output.write(' ')
                                output.write(piece_name)
                            output.write(COLUMN_CHARACTERS[column])
                            output.write(str(row + 1))
                
        
    def _get_piece_name(self, chessproblem, piece_type, piece_rotation):
        LOGGER.debug('Popeye._get_piece_name(..., %d, %d)' % (piece_type, piece_rotation))
        if piece_rotation == PIECE_ROTATION_NORMAL:
            return PIECE_CHARACTERS[piece_type].lower()
        else:
            # Search matching piecedef
            piecedef = self._find_piecedef(chessproblem, piece_type, piece_rotation)
            if piecedef != None:
                LOGGER.debug('Found PieceDef(%s,%s) for piecetype %s - piecerotation %s' % (piecedef.name, piecedef.piece_symbol, piece_type, piece_rotation))
                pt = self._memory_db_service.find_piecetype_by_name(piecedef.name)
                LOGGER.debug('Got PieceType(%s, %s) from PIECETYPE_SERVICE.' % (pt.get_name(), pt.get_popeye_name()))
                return pt.get_popeye_name()
            else:
                raise PopeyeException('Unspecified fairy piece: %s' % self._piece_symbol(piece_type, piece_rotation))

    def _piece_symbol(self, piece_type, piece_rotation):
        return PIECE_CHARACTERS[piece_type] + PIECE_ROTATIONS[piece_rotation - 1]

    def _find_piecedef(self, chessproblem, piece_type, piece_rotation):
        piece_symbol = self._piece_symbol(piece_type, piece_rotation)
        for result in chessproblem.piecedefs:
            if result.piece_symbol == piece_symbol:
                return result
        return None

def _ensure_popeye_directory(config):
    from os.path import exists
    if not exists(config.popeye_directory):
        from os import mkdir
        mkdir(config.popeye_directory)

DETACHED_PROCESS=0x00000008

def call_popeye(popeye_input, config):
    LOGGER.debug('call_popeye(%s)' % popeye_input)
    _ensure_popeye_directory(config)
    from datetime import datetime
    now = datetime.now()
    popeye_input_basename = now.strftime('%Y%m%d-%H%M%S')
    popeye_input_filename = '%s.inp' % popeye_input_basename
    popeye_output_filename = '%s.out' % popeye_input_basename
    from os.path import join
    popeye_input_file = join(config.popeye_directory, popeye_input_filename)
    import platform
    if platform.system() == 'Windows':
        from io import StringIO
        file_content = StringIO(popeye_input)
        with open(popeye_input_file, 'w') as f:
            for input_line in file_content:
                f.write(input_line)
                if input_line.startswith('anfangproblem'):
                    f.write('prot %s\n\n' % popeye_output_filename)
        # 
        import os
        os.chdir(config.popeye_directory)
        os.system('start "Popeye" /I cmd.exe /K %s %s' % (config.popeye_executable, popeye_input_filename))
    elif platform.system() == 'Linux':
        with open(popeye_input_file, 'w') as f:
            f.write(popeye_input)
        from subprocess import Popen
        Popen([config.popeye_executable, popeye_input_filename, popeye_output_filename], cwd=config.popeye_directory)

