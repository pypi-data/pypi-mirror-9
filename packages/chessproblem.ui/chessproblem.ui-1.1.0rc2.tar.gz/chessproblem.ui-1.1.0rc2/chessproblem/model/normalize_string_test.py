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

from .model_util import normalize_string
from .model_util import normalize_author_name

class NormalizeTest(unittest.TestCase):
    def test_normalize_string(self):
        self.assertEqual('abcdefghijklmnopqrstuvwxyz', normalize_string('abcdefghijklmnopqrstuvwxyz'))
        self.assertEqual('abcdefghijklmnopqrstuvwxyz', normalize_string('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.assertEqual('honing', normalize_string('H\\"oning'))
        self.assertEqual('kuss', normalize_string('Ku\\3'))
        self.assertEqual('osario', normalize_string('Osario '))
        self.assertEqual('ijololaaaeaeoeoe', normalize_string('\\"{\\i} \\H{\\j}\\o  \\l \O \L\\AA\\aa\\AE\\ae\\OE\\oe'))
        self.assertEqual('aouaouss', normalize_string('ÄÖÜäöüß'))

class NormalizeAuthorNameTest(unittest.TestCase):
    def test_normalize_author_name(self):
        self.assertEqual('honing, stefan', normalize_author_name('H\\"on{\i}ng', 'Stef\v{a}n'))
        self.assertEqual('honing, stefan', normalize_author_name('Höning', 'Stefan'))
        self.assertEqual('linss, torsten', normalize_author_name('Linß', '\\ProfDr{} Torsten'))
        self.assertEqual('linss, torsten', normalize_author_name('Lin{\\ss}', '\\ProfDr{} Torsten'))
