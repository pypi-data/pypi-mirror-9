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
This utility module provides initializations for test code running agains the MemoryDbService.
'''

import chessproblem.kph as kph
from .model_util import normalize_string

class MemoryDbTestUtil(object):
    def __init__(self, db_service):
        self._db_service = db_service
        self._init_database()

    def _update(self, stmt, params=None):
        sf = self._db_service.session_factory()
        con = sf.connection().connection
        c = con.cursor()
        if params == None:
            c.execute(stmt)
        else:
            c.execute(stmt, params)
        con.commit()

    def _query(self, query):
        sf = self._db_service.session_factory()
        con = sf.connection().connection
        c = con.cursor()
        c.execute(query)
        return [row for row in c]

    def _init_database(self):
        self._insert_piecetype(1, 'Nachtreiter', 'n')
        self._insert_piecetype(4711, 'Lion', 'li')
        self._insert_condition(2, 'Circe', 'circe')
        self._insert_condition(3, 'Madrasi', 'madrasi')
        self._insert_condition(4, 'Marscirce', 'marscirce')
        self._insert_condition(5, 'Gitterschach', 'gitterschach', 'gridchess_problem_action')
        
    def _insert_piecetype(self, id, name, popeye_name):
        normalized = normalize_string(name)
        self._update("insert into piecetypes (id, _name, _popeye_name, _search, _kph) values(%d, '%s', '%s', '%s', '%s')" % (id, name, popeye_name, normalized, kph.encode(normalized)))


    def _insert_condition(self, id, name, popeye_name, problem_action=None):
        normalized = normalize_string(name)
        if problem_action != None:
            self._update("insert into conditions (id, _name, _popeye_name, _search, _kph, _problem_action_name) values(%d, '%s', '%s', '%s', '%s', '%s')" % (id, name, popeye_name, normalized, kph.encode(normalized), problem_action))
        else:
            self._update("insert into conditions (id, _name, _popeye_name, _search, _kph) values(%d, '%s', '%s', '%s', '%s')" % (id, name, popeye_name, normalized, kph.encode(normalized)))


