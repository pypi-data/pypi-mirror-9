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



from chessproblem.tools import handle_document
from chessproblem.tools.schwalbe import SchwalbeUrdrucke
from chessproblem.io import ChessProblemLatexParser, write_latex
from chessproblem.model.memory_db import create_memory_db

from chessproblem.config import create_config

from argparse import ArgumentParser

usage = '''
This script may be used to add common entries to all diagrams in the given file.
The resulting diagrams are written to a new file with the extension ".new" appended.
'''
parser = ArgumentParser()

parser.add_argument('filename')
parser.add_argument('-i', '--issue', dest='issue', default=None,
        help='die heft nummer')
parser.add_argument('-m', '--month', dest='month', default=None,
        help='der monat des erscheinens')
parser.add_argument('-y', '--year', dest='year', default=None,
        help='das erscheinungsjahr')
parser.add_argument('-s', '--start_sourcenr', dest='start_sourcenr',
        default=None, help='die start problemnummer des urdruckteils')
parser.add_argument('-c', '--config_dir', dest='config_dir',
        help='specifies the configuration directory', default=None)

args = parser.parse_args()

if args.config_dir != None:
    cpe_config = create_config(args.config_dir)
else:
    cpe_config = create_config()



if (args.filename != None and args.issue != None and args.month != None
        and args.year != None and args.start_sourcenr != None):
    handler = SchwalbeUrdrucke(args.issue, args.month, args.year, args.start_sourcenr)
    memory_db_service = create_memory_db(cpe_config.config_dir)
    parser = ChessProblemLatexParser(cpe_config, memory_db_service)
    with open(args.filename) as f:
        document = parser.parse_latex_str(f.read())
        handle_document(document, handler)
        outputfile = args.filename + '.new'
        with open(outputfile, 'w') as f:
            write_latex(document, f)
else:
    parser.print_help()

