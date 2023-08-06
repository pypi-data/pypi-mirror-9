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
This module contains the service class to communicate with the memory-database.
'''

import sqlalchemy as sa
import sqlalchemy.orm as orm

import chessproblem.kph as kph

from .conditions import Condition, set_boolean_problem_action, gridchess_problem_action, verticalcylinder_problem_action, horizontalcylinder_problem_action
from .piecetypes import PieceType

from .model_util import normalize_string

from .db_util import before_persist_object_listener, on_load_object_listener

import logging

LOGGER = logging.getLogger('chessproblem.model.memory_db')

class MemoryDbService(object):
    def __init__(self, url):
        self.session_factory = self._create_session_factory(url)
        self._session = None

    def _get_session(self):
        if self._session == None:
            self._session = self.session_factory()
        return self._session

    def _create_metadata(self, engine):
        metadata = sa.MetaData(bind=engine)

        # Create a mapping for the Condition class
        conditions_table = sa.Table('conditions', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('_name', sa.String),
                sa.Column('_popeye_name', sa.String),
                sa.Column('_problem_action_name', sa.String),
                sa.Column('_search', sa.String, index=True),
                sa.Column('_kph', sa.String, index=True))
        orm.mapper(Condition, conditions_table)
        sa.event.listen(Condition, 'before_insert', before_persist_object_listener)
        sa.event.listen(Condition, 'before_update', before_persist_object_listener)
        sa.event.listen(Condition, 'load', on_load_object_listener)

        # Create a mapping for the PieceType class
        piecetypes_table = sa.Table('piecetypes', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('_name', sa.String),
                sa.Column('_popeye_name', sa.String),
                sa.Column('_search', sa.String, index=True),
                sa.Column('_kph', sa.String, index=True))
        orm.mapper(PieceType, piecetypes_table)
        sa.event.listen(PieceType, 'before_insert', before_persist_object_listener)
        sa.event.listen(PieceType, 'before_update', before_persist_object_listener)

        return metadata

    def _create_session_factory(self, url):
        self.engine = sa.create_engine(url)
        self.metadata = self._create_metadata(self.engine)
        self.metadata.create_all(self.engine)
        session = orm.sessionmaker(bind=self.engine)
        return session

    # Methods to access Condition's
    def store_condition(self, condition):
        store_conditions([condition])

    def store_conditions(self, conditions):
        session = self._get_session()
        session.add_all(conditions)
        session.commit()

    def get_all_conditions(self):
        session = self._get_session()
        conditions = session.query(Condition).order_by(Condition._search).all()
        return conditions

    def filter_conditions_by_name(self, name):
        if name == None or len(name) == 0:
            return self.get_all_conditions()
        else:
            search = normalize_string(name)
            session = self._get_session()
            conditions = (session.query(Condition)
                .filter(sa.or_(Condition._search.like('%' + search + '%'), Condition._kph == kph.encode(search)))
                .order_by(Condition._search).all())
            return conditions

    def get_condition_by_name(self, name):
        '''
        This method may be used as factory method for conditions while reading problems from files.
        We first tries to find an exact matching condition.
        If none is found, we try to find a condition with a matching search string.
        If this not found either, we return a new condition with the given name.
        '''
        if name == None or len(name) == 0:
            return None
        else:
            session = self._get_session()
            conditions = (session.query(Condition).filter(Condition._name == name).all())
            if len(conditions) == 1:
                LOGGER.debug('condition with name %s found' % (name))
                return conditions[0]
            search = normalize_string(name)
            conditions = (session.query(Condition).filter(Condition._search == search).all())
            if len(conditions) == 1:
                LOGGER.debug('condition with search %s for name %s found' % (search, name))
                return conditions[0]
            LOGGER.info('no condition found for name %s with search %s - creating new one' % (name, search))
            return Condition(name)

    # Methods to access PieceType's

    def store_piecetype(self, piecetype):
        store_piecetypes([piecetype])

    def store_piecetypes(self, piecetypes):
        session = self._get_session()
        session.add_all(piecetypes)
        session.commit()

    def get_all_piecetypes(self):
        session = self._get_session()
        return session.query(PieceType).order_by(PieceType._search).all()

    def filter_piecetypes_by_name(self, name):
        if name == None or len(name) == 0:
            return self.get_all_piecetypes()
        else:
            search = normalize_string(name)
            session = self._get_session()
            piecetypes = (session.query(PieceType)
                .filter(sa.or_(PieceType._search.like('%' + search + '%'), PieceType._kph == kph.encode(search)))
                .order_by(PieceType._search).all())
            return piecetypes

    def find_piecetype_by_name(self, name):
        LOGGER.debug('MemoryDbService.find_piecetype_by_name(%s)' % (name))
        if name == None or len(name) == 0:
            return None
        else:
            session = self._get_session()
            piecetypes = (session.query(PieceType).filter(PieceType._name == name).all())
            if len(piecetypes) == 1:
                pt = piecetypes[0]
                LOGGER.debug('PieceType(%s, %s) with name %s found' % (pt.get_name(), pt.get_popeye_name(), name))
                return pt
            else:
                return None
        
    def get_piecetype_by_name(self, name):
        '''
        This method may be used as factory method for piecetypes while reading problems from files.
        We first tries to find an exact matching piecetype.
        If none is found, we try to find a piecetype with a matching search string.
        If this not found either, we return a new piecetype with the given name.
        '''
        LOGGER.debug('get_piecetype_by_name(%s)' % (name))
        if name == None or len(name) == 0:
            return None
        else:
            session = self._get_session()
            piecetypes = (session.query(PieceType).filter(PieceType._name == name).all())
            if len(piecetypes) == 1:
                LOGGER.debug('piecetype with name %s found' % (name))
                return piecetypes[0]
            search = normalize_string(name)
            piecetypes = (session.query(PieceType).filter(PieceType._search == search).all())
            if len(piecetypes) == 1:
                LOGGER.debug('piecetype with search %s for name %s found' % (search, name))
                return piecetypes[0]
            LOGGER.info('no piecetype found for name %s with search %s - creating new one' % (name, search))
            return PieceType(name)


from os.path import realpath, dirname, join, exists


import shutil

CONDITIONS = []

def read_conditions(config_dir):
    _condition_config_template = join(dirname(realpath(__file__)), 'condition_config_template.py')
    _condition_config = join(config_dir, 'condition_config.py')
    if not exists(_condition_config):
        shutil.copy(_condition_config_template, _condition_config)
    my_globals = {
            'Condition':  Condition,
            'gridchess_problem_action': gridchess_problem_action,
            'horizontalcylinder_problem_action': horizontalcylinder_problem_action,
            'verticalcylinder_problem_action': verticalcylinder_problem_action}
    exec(compile(open(_condition_config).read(), _condition_config, 'exec'), my_globals)
    result = my_globals['CONDITIONS']
    LOGGER.debug('found %d conditions in user config file %s' % (len(result), _condition_config))
    return result

def read_piecetypes(config_dir):
    _piecetype_config_template = join(dirname(realpath(__file__)), 'piecetypes_config_template.py')
    _piecetype_config = join(config_dir, 'piecetype_config.py')
    if not exists(_piecetype_config):
        shutil.copy(_piecetype_config_template, _piecetype_config)
    my_globals = {'PieceType': PieceType}
    exec(compile(open(_piecetype_config).read(), _piecetype_config, 'exec'), my_globals)
    result = my_globals['PIECETYPES']
    LOGGER.debug('read_piecetypes(%s): found %d piecetypes in user config file %s' % (config_dir, len(result), _piecetype_config))
    return result

def create_memory_db(config_dir):
    result = MemoryDbService('sqlite:///:memory:')
    result.store_conditions(read_conditions(config_dir))
    result.store_piecetypes(read_piecetypes(config_dir))
    return result;


