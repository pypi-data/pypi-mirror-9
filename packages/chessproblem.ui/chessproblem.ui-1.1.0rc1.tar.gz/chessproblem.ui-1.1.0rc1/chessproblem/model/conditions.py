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
This module contains the model classes for conditions, which may be selected
within the user interface.
'''

import logging
LOGGER = logging.getLogger('chessproblem.model.conditions')

from .model_util import normalize_string

import chessproblem.kph as kph

def set_boolean_problem_action(chessproblem, member, value=True):
    LOGGER.debug('set_boolean_problem_action(...,%s, %s)' % (member, str(value)))
    setattr(chessproblem, member, value)

def gridchess_problem_action(chessproblem):
    set_boolean_problem_action(chessproblem, 'gridchess')

def verticalcylinder_problem_action(chessproblem):
    set_boolean_problem_action(chessproblem, 'verticalcylinder')

def horizontalcylinder_problem_action(chessproblem):
    set_boolean_problem_action(chessproblem, 'horizontalcylinder')

CONDITION_ACTIONS = {
    'gridchess_problem_action':  gridchess_problem_action,
    'verticalcylinder_problem_action': verticalcylinder_problem_action,
    'horizontalcylinder_problem_action': horizontalcylinder_problem_action }

class Condition(object):
    '''
    Stores a fairy condition.
    Each fairy condition consists of:
    -   a name (which is the LaTeX encoded text used in documents)
    -   an optional keyword to use with popeye
    -   an optional problem_action, which allows e.g. to automatically set
        gridchess to 'True'. This must be a method, which expects a single 'Chessproblem'
        instances as parameter.
    '''
    def __init__(self, name, popeye_name=None, problem_action=None):
        '''
        Creates a fairy condition with the given 'name'.
        '''
        self._name = name
        self._popeye_name = popeye_name
        self._problem_action = problem_action
        self._problem_action_name = None

    def get_name(self):
        '''
        Retrieve the 'name' of the condition.
        '''
        return self._name

    def get_popeye_name(self):
        return self._popeye_name

    def get_search(self):
        return self._search

    def get_kph(self):
        return self._kph

    def execute_problem_action(self, chessproblem):
        '''
        Executes the registered '_problem_action'.
        '''
        if self._problem_action != None:
            self._problem_action(chessproblem)

    def on_persist(self):
        self._search = normalize_string(self._name)
        self._kph = kph.encode(self._search)
        if self._problem_action == None:
            self._problem_action_name = None
        elif self._problem_action == gridchess_problem_action:
            self._problem_action_name = 'gridchess_problem_action'
        elif self._problem_action == verticalcylinder_problem_action:
            self._problem_action_name = 'verticalcylinder_problem_action' 
        elif self._problem_action == horizontalcylinder_problem_action:
            self._problem_action_name = 'horizontalcylinder_problem_action'
        else:
            raise Exception('unknown problem action ' + str(self._problem_action))

    def on_load(self):
        if self._problem_action_name != None:
            self._problem_action = CONDITION_ACTIONS[self._problem_action_name]
        else:
            self._problem_action = None

    def __str__(self):
        return self._name

