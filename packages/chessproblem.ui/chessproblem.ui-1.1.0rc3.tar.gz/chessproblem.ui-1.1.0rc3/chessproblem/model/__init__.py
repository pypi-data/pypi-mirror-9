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

"""
This package implements the internal chessproblem (representation) model.
"""

import logging

import re

import chessproblem.kph as kph

from .model_util import normalize_string
from .model_util import normalize_author_name

LOGGER = logging.getLogger('chessproblem.model')

PIECE_TYPE_PAWN       = 0
PIECE_TYPE_KNIGHT     = 1
PIECE_TYPE_BISHOP     = 2
PIECE_TYPE_ROOK       = 3
PIECE_TYPE_QUEEN      = 4
PIECE_TYPE_KING       = 5
PIECE_TYPE_EQUIHOPPER = 6
PIECE_TYPE_CIRCLE     = 7
PIECE_TYPE_COUNT      = 8

NORMAL_PIECE_TYPE_COUNT = 6

PIECE_COLOR_WHITE   = 0
PIECE_COLOR_BLACK   = 1
PIECE_COLOR_NEUTRAL = 2
PIECE_COLOR_COUNT   = 3

PIECE_ROTATION_NORMAL       = 0
PIECE_ROTATION_LEFT         = 1
PIECE_ROTATION_RIGHT        = 2
PIECE_ROTATION_UPSIDEDOWN   = 3
PIECE_ROTATION_COUNT        = 4

import string


class Piece(object):
    '''
    Stores the type of the piece.
    '''
    def __init__(self, piece_color, piece_type, piece_rotation=PIECE_ROTATION_NORMAL):
        self.piece_color = piece_color
        self.piece_type = piece_type
        self.piece_rotation = piece_rotation

class Country(object):
    '''
    Stores the country, where authors live.
    A list of these "car codes" including a list of ISO 3166 Country codes (2-letter, 3-letter and numeric) can be found
    at: http://www.aufenthaltstitel.de/staaten/schluessel.html
    '''
    def __init__(self, car_code, name=None, iso_3166_2=None, iso_3166_3=None, iso_3166_n=None):
        self.car_code = car_code
        self.name = name
        self.iso_3166_2 = iso_3166_2
        self.iso_3166_3 = iso_3166_3
        self.iso_3166_n = iso_3166_n
        self.search = None

    def on_persist(self):
        '''
        This method is is configured to be called automatically by sqlalchemhy.
        We use it to normalize the car_code column and to create the value for the search column.
        '''
        if self.car_code != None:
            self.car_code = self.car_code.upper()
        if self.name == None:
            self.search = ''
        else:
            self.search = normalize_string(self.name)

    def code(self):
        '''
        Our preferred code is the car_code.
        As not all countries in the world have a car code, we use the 3-letter iso code for such countries.
        '''
        if self.car_code != None:
            return self.car_code
        else:
            return self.iso_3166_3

    def __str__(self):
        if self.name != None:
            return '(' + self.code() + ') ' + self.name
        else:
            return '(' + self.code() + ') '

class City(object):
    '''
    Stores the city, where an author lives.
    '''
    def __init__(self, name, country=None):
        self.name = name
        self.search = None
        self.country = country

    def on_persist(self):
        '''
        This method is is configured to be called automatically by sqlalchemhy
        to calculate the value of the search column.
        '''
        if self.name == None:
            self.search = ''
            self.kph = ''
        else:
            self.search = normalize_string(self.name)
            self.kph = kph.encode(self.search)

    def __str__(self):
        '''
        This method creates a string representation including the country if available.
        '''
        if self.country != None:
            return self.country_code() + '--' + self.name
        else:
            return self.name

    def country_code(self):
        if self.country != None:
            return self.country.code()
        else:
            return ''

    def country_name(self):
        if self.country != None:
            return self.country.name
        else:
            return ''


class Author(object):
    '''
    Stores the author of a chessproblem.
    '''
    def __init__(self, lastname=None, firstname=None, city=None):
        self.lastname = lastname
        self.firstname = firstname
        self.city = city
        self.search = None

    def on_persist(self):
        '''
        This method is is configured to be called automatically by sqlalchemhy
        to calculate the value of the search column.
        '''
        self.search = normalize_author_name(self.lastname, self.firstname)
        self.lastname_kph = kph.encode(self.lastname)
        self.firstname_kph = kph.encode(self.firstname)

    def __str__(self):
        namestr = str(self.lastname) + ', ' + str(self.firstname)
        if self.city == None:
            return namestr
        else:
            return namestr + '[' + str(self.city) + ']'


class PieceCounter(object):
    '''
    Used to count pieces.
    '''
    def __init__(self, count_white=0, count_black=0, count_neutral=0):
        '''
        Initially all counters are set to 0.
        '''
        self.count_white = count_white
        self.count_black = count_black
        self.count_neutral = count_neutral


class Field(object):
    '''
    Stores contents and other attributes of a field.
    '''
    def __init__(self):
        '''
        Initially a field is empty.
        '''
        self._piece = None
        self._has_frame = False
        self._nofield = False

    def get_piece(self):
        '''
        Retrieve the piece placed on the field.
        '''
        return self._piece

    def set_piece(self, piece):
        '''
        Place the given piece on the field.
        '''
        self._piece = piece

    def has_frame(self):
        return self._has_frame

    def set_has_frame(self, has_frame):
        self._has_frame = has_frame

    def toggle_frame(self):
        '''
        Used to toggle field frame value.
        '''
        self._has_frame = not self._has_frame

    def is_nofield(self):
        return self._nofield

    def set_nofield(self, nofield):
        self._nofield = nofield

    def toggle_nofield(self):
        self._nofield = not self._nofield

class Board(object):
    '''
    Stores the position of the board.
    '''
    def __init__(self, rows=8, columns=8):
        self.rows = rows
        self.columns = columns
        self.fields = [[Field() for column in range(0, columns)] for row in range(0, rows)]

    def resize(self, new_rows, new_columns):
        '''
        Change the size of the board to the new size and reuse the old position where possible.
        '''
        new_fields =  [[Field() for column in range(0, new_columns)] for row in range(0, new_rows)]
        if new_rows > self.rows:
            max_rows = self.rows
        else:
            max_rows = new_rows
        if new_columns > self.columns:
            max_columns = self.columns
        else:
            max_columns = new_columns
        for row in range(0, max_rows):
            for column in range(0, max_columns):
                new_fields[row][column] = self.fields[row][column]
        self.rows = new_rows
        self.columns = new_columns
        self.fields = new_fields

    def get_pieces_count(self):
        white = 0
        black = 0
        neutral = 0
        for row in range(0, self.rows):
            for column in range(0, self.columns):
                field = self.fields[row][column]
                if not field.is_nofield():
                    piece = field.get_piece()
                    if piece != None:
                        if piece.piece_color == PIECE_COLOR_WHITE:
                            white += 1
                        elif piece.piece_color == PIECE_COLOR_BLACK:
                            black += 1
                        elif piece.piece_color == PIECE_COLOR_NEUTRAL:
                            neutral += 1
        return (white, black, neutral)

class PieceDef(object):
    '''
    Stores the explanation for a rotated piece.
    The explanation consists of the 'piece_symbol', which is e.g. 'SU' for an
    upsidedown knight; the name of the piece, e.g. 'Nachtreiter', and the colors
    which in which the piece is displayed.
    '''
    def __init__(self, colors, piece_symbol, name):
        self.colors = colors
        self.piece_symbol = piece_symbol
        self.name = name

    def __repr__(self):
        return 'PieceDef(%s, %s, %s)' % (self.colors, self.piece_symbol, self.name)

class GridLine(object):
    '''
    Stores information about a single entry within the \gridlines{...} command.
    '''
    def __init__(self, orientation, x, y, length):
        self.orientation = orientation
        self.x = x
        self.y = y
        self.length = length

    def __str__(self):
        if self.orientation == None:
            raise Exception('Uninitialized GridLine')
        if self.x >= 10:
            x_str = '{%d}' % self.x
        else:
            x_str = str(self.x)
        if self.y >= 10:
            y_str = '{%d}' % self.y
        else:
            y_str = str(self.y)
        if self.length >= 10:
            length_str = '{%d}' % self.length
        else:
            length_str = str(self.length)
        return '%s%s%s%s' % (self.orientation, x_str, y_str, length_str)

class FieldText(object):
    '''
    Stores information about text to be displayed on fields.
    '''
    def __init__(self, text, column, row):
        self.text = text
        self.column = column
        self.row = row

class Chessproblem(object):
    '''
    Stores all information about a chessproblem.
    '''
    def __init__(self, rows=8, columns=8):
        self.board = Board(rows, columns)
        self.after_command_text = { '{diagram}': '%\n'}
        self.authors = []
        self.cities = []
        self.dedication = None
        self.after = None
        self.version = None
        self.stipulation = None
        self.condition = []
        self.twins = []
        self.remark = None
        self.solution = None
        self.themes = []
        self.comment = None
        self.specialdiagnum = None
        self.sourcenr = None
        self.source = None
        self.issue = None
        self.pages = None
        self.day = None
        self.month = None
        self.year = None
        self.tournament = None
        self.award = None
        self.verticalcylinder = False
        self.horizontalcylinder = False
        self.gridchess = False
        self.noframe = False
        self.nofields = None
        self.gridlines = []
        self.fieldtext = []
        self.pieces_control = None
        self.allwhite = False
        self.switchcolors = False
        self.piecedefs = []
        self.Co = None
        self.label = None

def _is_chessproblem(o):
    return isinstance(o, Chessproblem)

def _is_text(o):
    return isinstance(o, str) or isinstance(o, str)

class ChessproblemDocument(object):
    '''
    This class will contain list where an element is either a 'Chessproblem' or a string (normal or unicode).
    '''
    def __init__(self, document_content = None):
        if document_content == None:
            self.document_content = ['%\n', Chessproblem(), '%\n%\n']
        else:
            self.document_content = document_content

    def __iter__(self):
        return iter(self.document_content)

    def get_problem(self, index):
        return self._get_typed_element(index, _is_chessproblem)

    def get_text(self, index):
        return self._get_typed_element(index, _is_text)

    def _get_internal_index(self, index, check):
        found_index = -1
        for internal_index in range(len(self.document_content)):
            element = self.document_content[internal_index]
            if check(element):
                found_index += 1
                if found_index == index:
                    return internal_index
        return -1

    def _get_typed_element(self, index, check):
        internal_index = self._get_internal_index(index, check)
        if internal_index == -1:
            return None
        else:
            return self.document_content[internal_index]


    def get_problem_count(self):
        '''
        Return the number of problems contained in this document.
        '''
        return self._get_count(_is_chessproblem)

    def _get_count(self, check):
        count = 0
        for element in self.document_content:
            if check(element):
                count += 1
        return count

    def insert_problem(self, index, problem):
        '''
        Inserts the given problem before the problem with the given (problem) index.
        '''
        if index == self.get_problem_count():
            if self.get_problem_count() == 0:
                internal_index = 0
                LOGGER.debug('insert_problem: no problems in document')
            else:
                internal_index = len(self.document_content)
                LOGGER.debug('insert_problem: new last problem')
        else:
            internal_index = self._get_internal_index(index, _is_chessproblem)
        LOGGER.debug('insert_problem: insert_index = ' + str(internal_index))
        self.document_content.insert(internal_index, '%\n%\n%\n')
        self.document_content.insert(internal_index, problem)

    def set_problem(self, index, problem):
        '''
        Replace the problem with the given (problem) index with the given problem.
        '''
        internal_index = self._get_internal_index(index, _is_chessproblem)
        self.document_content[internal_index] = problem

    def delete_problem(self, index):
        '''
        Delete the problem with the given (problem) index.
        '''
        internal_index = self._get_internal_index(index, _is_chessproblem)
        self.document_content.pop(internal_index)

    def get_text_count(self):
        '''
        Return the number of text sections within the this document.
        '''
        return self._get_count(_is_text)

class ChessProblemModelFactory(object):
    '''
    Factory to create chesspbroblem model objects.
    '''
    def create_country(self, car_code, name=None):
        '''
        Creates a country object with the specified abbreviation.
        '''
        return Country(car_code, name)

    def create_city(self, country, city_name):
        '''
        Creates a city object with the given city_name and a reference to the given country.
        '''
        return City(city_name, country)

    def create_author(self, city, lastname, firstname):
        '''
        Creates an author object, with the given firstname and lastname, which refers to the given city.
        '''
        return Author(lastname, firstname, city)


class Source(object):
    '''
    The name of a book, magazine, newspaper (or even tournament) where a problem was published first.
    '''
    def __init__(self, name):
        '''
        Registers the name of the source.
        '''
        self.name = name

    def on_persist(self):
        '''
        '''
        self.search = normalize_string(self.name)
        self.kph = kph.encode(self.search)

def countries_equal(c1, c2):
    if c1 == c2:
        return True
    elif c1 == None or c2 == None:
        return False
    else:
        result = c1.iso_3166_3 == c2.iso_3166_3
        LOGGER.debug('countries_equal(..) -> %r' % result)
        return result

def cities_equal(c1, c2):
    if c1 == c2:
        return True
    elif c1 == None or c2 == None:
        return False
    else:
        result = c1.name == c2.name and countries_equal(c1.country, c2.country)
        LOGGER.debug('cities_equal(..) -> %r' % result)
        return result

def authors_equal(a1, a2):
    if a1 == a2:
        return True
    elif a1 == None or a2 == None:
        return False
    else:
        result = (a1.lastname == a2.lastname
                and a1.firstname == a2.firstname
                and cities_equal(a1.city, a2.city))
        LOGGER.debug('authors_equal(..) -> %r' % result)
        return result

def piecedefs_equal(p1, p2):
    if p1 == p2:
        return True
    elif p1 == None or p2 == None:
        return False
    else:
        result = (p1.colors == p2.colors
                and p1.piece_symbol == p2.piece_symbol
                and p1.name == p2.name)
        LOGGER.debug('piecedefs_equal(..) -> %r' % result)
        return result

def pieces_equal(p1, p2):
    if p1 == p2:
        return True
    elif p1 == None or p2 == None:
        return False
    else:
        result = (p1.piece_color == p2.piece_color
                and p1.piece_type == p2.piece_type
                and p2.piece_rotation == p2.piece_rotation)
        LOGGER.debug('pieces_equal(..) -> %r' % result)
        return result

def fields_equal(f1, f2):
    if f1 == f2:
        return True
    elif f1 == None or f2 == None:
        return False
    else:
        result = (f1.has_frame() == f2.has_frame()
                and f1.is_nofield() == f2.is_nofield()
                and pieces_equal(f1.get_piece(), f2.get_piece()))
        LOGGER.debug('fields_equal(..) -> %r' % result)
        return result

def piececounters_equal(p1, p2):
    if p1 == p2:
        return True
    elif p1 == None or p2 == None:
        return False
    else:
        result = (p1.count_white == p2.count_white
                and p1.count_black == p2.count_black
                and p1.count_neutral == p2.count_neutral)
        LOGGER.debug('piececounters_equal(..) -> %r' % result)
        return result

def boards_equal(b1, b2):
    if b1 == b2:
        return True
    elif b1 == None or b2 == None:
        return False
    elif b1.rows != b2.rows or b1.columns != b2.columns:
        return False
    else:
        for row in range(b1.rows):
            for column in range(b1.columns):
                if not fields_equal(b1.fields[row][column], b2.fields[row][column]):
                    LOGGER.debug('_boards_equal(..) [%d][%d] -> False' % (row, column))
                    return False
        return True

def _conditions_equal(c1, c2):
    result = c1.get_name() == c2.get_name()
    LOGGER.debug('_conditions_equal() -> %r' % result)
    return result

def _gridlines_equal(g1, g2):
    if g1 == g2:
        return True
    elif g1 == None or g2 == None:
        return False
    else:
        result = g1.x == g2.x and g1.y == g2.y and g1.length == g2.length
        LOGGER.debug('_gridlines_equal(%s, %s) -> %r' % (g1, g2, result))
        return result

def _fieldtexts_equal(f1, f2):
    if f1 == f2:
        return True
    elif f1 == None or f2 == None:
        return False
    else:
        result = f1.text == f2.text and f1.column == f2.column and f1.row == f2.row
        LOGGER.debug('_gridlines_equal(%r, %r) -> %r' % (f1, f2, result))
        return result

def _simple_equal(o1, o2):
    result = o1 == o2
    LOGGER.debug('_simple_equal(%s, %s) -> %r' % (str(o1), str(o2), result))
    return result

def _lists_equal(l1, l2, member_comparator=_simple_equal):
    if l1 == l2:
        return True
    elif len(l1) != len(l2):
        LOGGER.debug('_lists_equal(..) len(l1) != len(l2)')
        return False
    else:
        for i in range(len(l1)):
            if not member_comparator(l1[i], l2[i]):
                LOGGER.debug('_lists_equal(..) [%d] %s != %s -> False' % (i, str(l1[i]), str(l2[i])))
                return False
        return True

def _members_equal(o1, o2, member_name):
    member1 = getattr(o1, member_name)
    member2 = getattr(o2, member_name)
    result =  member1 == member2
    LOGGER.debug('_members_equal(o1:%r, o2:%r, ''%s'' -> %r' % (member1, member2, member_name, result))
    return result


CHESSPROBLEM_TEXT_MEMBERS = [
        # Simple string members
        'dedication', 
        'after', 
        'version', 
        'stipulation', 
        'remark', 
        'solution', 
        'comment', 
        'specialdiagnum', 
        'sourcenr', 
        'source', 
        'issue', 
        'pages', 
        'day', 
        'month', 
        'year', 
        'tournament', 
        'award', 
        'Co',
        'label' ]

CHESSPROBLEM_BOOLEAN_MEMBERS = [
        # Simple boolean members
        'verticalcylinder', 
        'horizontalcylinder', 
        'noframe', 
        'gridchess', 
        'allwhite', 
        'switchcolors' ]

def chessproblems_equal(cp1, cp2):
    if cp1 == cp2:
        LOGGER.debug('chessproblems_equal() -> True')
        return True
    elif cp1 == None or cp2 == None:
        LOGGER.debug('chessproblems_equal() -> False')
        return False
    else: 
        # Compare boolean members
        for boolean_member in CHESSPROBLEM_BOOLEAN_MEMBERS:
            if not _members_equal(cp1, cp2, boolean_member):
                LOGGER.debug('chessproblems_equal() %s -> False' % boolean_member)
                return False
        # Compare text members
        for text_member in CHESSPROBLEM_TEXT_MEMBERS:
            if not _members_equal(cp1, cp2, text_member):
                LOGGER.debug('chessproblems_equal() %s -> False' % text_member)
                return False
        # String list members
        if not _lists_equal(cp1.twins, cp2.twins):
            LOGGER.debug('chessproblems_equal() twins -> False')
            return False
        if not _lists_equal(cp1.themes, cp2.themes):
            LOGGER.debug('chessproblems_equal() themes -> False')
            return False
        # Conditions
        if not _lists_equal(cp1.condition, cp2.condition, _conditions_equal):
            LOGGER.debug('chessproblems_equal() condition -> False')
            return False
        # Authors
        if not _lists_equal(cp1.authors, cp2.authors, authors_equal):
            LOGGER.debug('chessproblems_equal() authors -> False')
            return False
        # Cities
        if not _lists_equal(cp1.cities, cp2.cities, cities_equal):
            LOGGER.debug('chessproblems_equal() cities -> False')
            return False
        # PieceDefs
        if not _lists_equal(cp1.piecedefs, cp2.piecedefs, piecedefs_equal):
            LOGGER.debug('chessproblems_equal() piecedefs -> False')
            return False
        # PieceCounter
        if not piececounters_equal(cp1.pieces_control, cp2.pieces_control):
            LOGGER.debug('chessproblems_equal() pieces_control -> False')
            return False
        # gridlines
        if not _lists_equal(cp1.gridlines, cp2.gridlines, _gridlines_equal):
            LOGGER.debug('chessproblems_equal() gridlines -> False')
            return False
        # fieldtexts
        if not _lists_equal(cp1.fieldtext, cp2.fieldtext, _fieldtexts_equal):
            LOGGER.debug('chessproblems_equal() fieldtext -> False')
            return False
        # Board
        if not boards_equal(cp1.board, cp2.board):
            LOGGER.debug('chessproblems_equal() board -> False')
            return False
        # Nothing different
        LOGGER.debug('chessproblems_equal() -> True')
        return True

