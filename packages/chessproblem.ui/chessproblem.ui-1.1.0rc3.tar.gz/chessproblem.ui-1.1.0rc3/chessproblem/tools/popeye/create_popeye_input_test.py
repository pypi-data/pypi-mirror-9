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
This module contains testcases for the popeye input creation.
'''

import unittest

import logging

filehandler = logging.FileHandler('create_popeye_input.log')

popeye_logger = logging.getLogger('chessproblem.tools.popeye')
popeye_logger.setLevel(logging.DEBUG)
popeye_logger.addHandler(filehandler)

memory_db_logger = logging.getLogger('chessproblem.model.memory_db')
memory_db_logger.setLevel(logging.DEBUG)
memory_db_logger.addHandler(filehandler)

LOGGER = popeye_logger

from chessproblem.config import create_config

from chessproblem.model import Chessproblem

from chessproblem.io import ChessProblemLatexParser

from chessproblem.tools.popeye import Popeye

from sqlalchemy.orm import clear_mappers

from chessproblem.model.memory_db import create_memory_db

from chessproblem.model.memory_db_test_util import MemoryDbTestUtil

class CreatePopeyeInputTest(unittest.TestCase):
    def setUp(self):
        self.cpe_config = create_config()
        clear_mappers()
        self.db_service = create_memory_db(self.cpe_config.config_dir)
        self.parser = ChessProblemLatexParser(self.cpe_config, self.db_service)
        self.popeye = Popeye(self.db_service)

    def test_empty_problem(self):
        self.assertEqual('anfangproblem\n\nforderung \n\n\nendeproblem\n', self.popeye.create_popeye_input(Chessproblem()))
        
    def test_mate_problem(self):
        cp = Chessproblem()
        cp.stipulation = '\\#5'
        self.assertEqual('anfangproblem\n\nforderung #5\n\n\nendeproblem\n', self.popeye.create_popeye_input(cp))

    def test_double_mate_problem(self):
        cp = Chessproblem()
        cp.stipulation = '\\#\\#3'
        self.assertEqual('anfangproblem\n\nforderung ##3\n\n\nendeproblem\n', self.popeye.create_popeye_input(cp))

    def test_vvp(self):
        cp = self._create_problem_from_string('\\begin{diagram}\stip{\\#1}\\pieces{wKc8, wBb6, sKa8, sBa7}\\end{diagram}')
        self.assertEqual('anfangproblem\n\nforderung #1\n\nsteine\nweiss   kc8 bb6\nschwarz ka8 ba7\n\nendeproblem\n',
                self.popeye.create_popeye_input(cp))

    def test_with_nachtreiter_and_lion(self):
        cp = self._create_problem_from_string('\\begin{diagram}\stip{\\#1}\\pieces{wKe1, sKe7, wSUe4, nTLb5}\\piecedefs{{w}{SU}{Nachtreiter}; {n}{TL}{Lion}}\\end{diagram}')
        self.assertEqual('anfangproblem\n\nforderung #1\n\nsteine\nweiss   ke1 ne4\nschwarz ke7\nneutral lib5\n\nendeproblem\n',
                self.popeye.create_popeye_input(cp))

    def _create_problem_from_string(self, string):
        document = self.parser.parse_latex_str(string)
        return document.get_problem(0)

if __name__ == "__main__":
    unittest.main()

