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
This module contains the model classes for piecetypes, which may be selected
within the user interface.
'''

from .model_util import normalize_string

import chessproblem.kph as kph

class PieceType(object):
    '''
    A piecetype specifies a fairy piece type.
    The type consists of a name and the short form used within popeye.
    '''
    def __init__(self, name, popeye_name):
        self._name = name
        self._popeye_name = popeye_name

    def get_name(self):
        return self._name

    def get_popeye_name(self):
        return self._popeye_name

    def on_persist(self):
        self._search = normalize_string(self._name)
        self._kph = kph.encode(self._search)

    def __repr__(self):
        return 'PieceType(%s,%s)' % (self._name, self._popeye_name)

    def __str__(self):
        return self._name

    def get_search(self):
        return self._search

    def get_kph(self):
        return self.kph

