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
This module contains testcases for the piecetypes service.
'''

import unittest

import logging

LOGGER = logging.getLogger('chessproblem.model.memory_db_test')
LOGGER.setLevel(logging.DEBUG)
filehandler = logging.FileHandler('memory_db_test.log')
LOGGER.addHandler(filehandler)

from sqlalchemy.orm import clear_mappers

from .memory_db import MemoryDbService

from .memory_db_test_util import MemoryDbTestUtil

class MemoryDbServiceTest(unittest.TestCase):
    def setUp(self):
        clear_mappers()
        self.db_service = MemoryDbService('sqlite:///:memory:')
        self.test_util = MemoryDbTestUtil(self.db_service)

    def test_find_Nachtreiter(self):
        piecetype = self.db_service.get_piecetype_by_name('Nachtreiter')
        self.assertEqual('Nachtreiter', piecetype.get_name())
        self.assertEqual('n', piecetype.get_popeye_name())

    def test_get_all_conditions(self):
        conditions = self.db_service.get_all_conditions()
        self.assertTrue(conditions != None)
        self.assertTrue(3, len(conditions))

    def test_filter_circe_conditions(self):
        conditions = self.db_service.filter_conditions_by_name('circ')
        self.assertTrue(conditions != None)
        self.assertEqual(2, len(conditions))

    def test_get_condition_by_name(self):
        circe = self.db_service.get_condition_by_name('Circe')
        self.assertEqual('Circe', circe.get_name())
        self.assertEqual('circe', circe.get_popeye_name())


if __name__ == '__main__':
    unittest.main()

