#!/usr/bin/env python

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



from chessproblem.config import create_config

def cpdb_ui(cpe_config):
    '''
    Starts the chessproblem basedata user interface.
    '''
    from chessproblem.ui.database import MainFrame
    frame = MainFrame(cpe_config)
    frame.main()

def cpdb_import(cpe_config, filename):
    '''
    Starts the dialog to import basedata from latex files.
    '''
    from chessproblem.ui.database.file_importer import import_all_from_tex
    from chessproblem.model.db import DbService
    db_service = DbService(cpe_config.database_url)
    import_all_from_tex(db_service, filename)

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-i', '--import', dest='import_filename',
        default=None, help='import data from latex file')
parser.add_argument('-c', '--config_dir', dest='config_dir',
        help='specifies the configuration directory', default=None)

args = parser.parse_args()

if args.config_dir != None:
    cpe_config = create_config(args.config_dir)
else:
    cpe_config = create_config(None)

if args.import_filename != None:
    cpdb_import(cpe_config, args.import_filename)
else:
    cpdb_ui(cpe_config)
