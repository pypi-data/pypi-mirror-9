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

from chessproblem.model import *
from chessproblem.model import _members_equal, _lists_equal

import unittest

class MemberEqualsTest(unittest.TestCase):
    def setUp(self):
        self.o1 = Chessproblem()
        self.o1.stipulation = 'H\\#2'
        self.o1.remark = 'Cook'
        self.o2 = Chessproblem()
        self.o2.stipulation = 'H\\#2'
        self.o2.remark = None

    def test_equal_members(self):
        self.assertEquals(True, _members_equal(self.o1, self.o2, 'stipulation'))

    def test_nonequal_members(self):
        self.assertEquals(False, _members_equal(self.o1, self.o2, 'remark'))

class ListsEqualTest(unittest.TestCase):
    def setUp(self):
        self.list1 = []
        self.list2 = ['Hello World', 'Good Morning']
        self.list3 = ['Hello World', 'Good Evening']
        self.list4 = ['Schach', 'Matt', 'Patt']

    def test_self(self):
        self.assertEquals(True, _lists_equal(self.list1, self.list1))
        self.assertEquals(True, _lists_equal(self.list2, self.list2))
        self.assertEquals(True, _lists_equal(self.list3, self.list3))
        self.assertEquals(True, _lists_equal(self.list4, self.list4))

    def test_different_size(self):
        self.assertEquals(False, _lists_equal(self.list1, self.list2))
        self.assertEquals(False, _lists_equal(self.list1, self.list3))
        self.assertEquals(False, _lists_equal(self.list1, self.list4))
        self.assertEquals(False, _lists_equal(self.list2, self.list4))
        self.assertEquals(False, _lists_equal(self.list3, self.list4))

    def test_different_values(self):
        self.assertEquals(False, _lists_equal(self.list2, self.list3))


class CountriesEqualTest(unittest.TestCase):
    def setUp(self):
        self.country1 = Country('USA')
        self.country1.iso_3166_3 = 'USA'
        self.country2 = Country('D')
        self.country2.iso_3166_3 = 'GER'

    def test_self_equals(self):
        self.assertEquals(True, countries_equal(self.country1, self.country1))
        self.assertEquals(True, countries_equal(self.country2, self.country2))

    def test_countries_differ(self):
        self.assertEquals(False, countries_equal(self.country1, self.country2))

class CitiesEqualTest(unittest.TestCase):
    def setUp(self):
        self.country1 = Country('USA')
        self.country1.iso_3166_3 = 'USA'
        self.country2 = Country('D')
        self.country2.iso_3166_3 = 'GER'
        self.city1 = City('Ulm', self.country1)
        self.city2 = City('Ulm', self.country2)
        self.city3 = City('Regensburg', self.country2)

    def test_self_equals(self):
        self.assertEquals(True, cities_equal(self.city1, self.city1))
        self.assertEquals(True, cities_equal(self.city2, self.city2))
        self.assertEquals(True, cities_equal(self.city3, self.city3))

    def test_different_name(self):
        self.assertEquals(False, cities_equal(self.city1, self.city3))

    def test_different_country(self):
        self.assertEquals(False, cities_equal(self.city1, self.city2))

class AuthorsEqualTest(unittest.TestCase):
    def setUp(self):
        self.country1 = Country('D')
        self.country1.iso_3166_3 = 'GER'
        self.city1 = City('Ulm', self.country1)
        self.city2 = City('Regensburg', self.country1)
        self.author1 = Author()
        self.author1.lastname = 'Gruber'
        self.author1.firstname = 'Hans'
        self.author1.city = self.city1
        self.author2 = Author()
        self.author2.lastname = 'Gruber'
        self.author2.firstname = '\\ProfDr{} Hans'
        self.author2.city = self.city1
        self.author3 = Author()
        self.author3.lastname = 'Gruber'
        self.author3.firstname = 'Hans'
        self.author3.city = self.city2
        self.author4 = Author()
        self.author4.lastname = 'ellinghoven'
        self.author4.firstname = 'Hans'
        self.author4.city = self.city2

    def test_self_equals(self):
        self.assertEquals(True, authors_equal(self.author1, self.author1))
        self.assertEquals(True, authors_equal(self.author2, self.author2))
        self.assertEquals(True, authors_equal(self.author3, self.author3))

    def test_different_lastname(self):
        self.assertEquals(False, authors_equal(self.author1, self.author4))
        self.assertEquals(False, authors_equal(self.author2, self.author4))
        self.assertEquals(False, authors_equal(self.author3, self.author4))

    def test_different_firstname(self):
        self.assertEquals(False, authors_equal(self.author2, self.author1))
        self.assertEquals(False, authors_equal(self.author2, self.author3))

    def test_different_city(self):
        self.assertEquals(False, authors_equal(self.author1, self.author3))

class ChessproblemsEqualTest(unittest.TestCase):
    def setUp(self):
        self.chessproblem1 = Chessproblem()
        self.chessproblem2 = Chessproblem()

    def test_self_equals(self):
        self.assertEquals(True, chessproblems_equal(self.chessproblem1, self.chessproblem1))

    def test_none_not_equals(self):
        self.assertEquals(False, chessproblems_equal(self.chessproblem1, None))
        self.assertEquals(False, chessproblems_equal(None, self.chessproblem1))

