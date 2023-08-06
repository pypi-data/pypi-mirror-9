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


from argparse import ArgumentParser

from chessproblem.io import ChessProblemLatexParser
from chessproblem.model.memory_db import create_memory_db
from chessproblem.config import create_config
from chessproblem.tools.images import create_image

parser = ArgumentParser(description='Converts LaTeX chess-problem-diagrams to Fairy FEN.')

parser.add_argument('filename')
parser.add_argument('-c', '--config_dir', dest='config_dir',
        help='specifies the configuration directory', default=None)
parser.add_argument('-s', '--pixel_size', dest='pixel_size', type=int, choices=[32, 36, 40, 44, 48],
        help='''specifies the pixel size of the single piece images to use.
Valid values are: 32, 36, 40, 44, 48''', default='40')

args = parser.parse_args()

if args.config_dir != None:
    cpe_config = create_config(args.config_dir)
else:
    cpe_config = create_config(None)

def generate_png_files(document, image_pixel_size, filename_prefix):
    for index in range(document.get_problem_count()):
        chessproblem = document.get_problem(index)
        try:
            image = create_image(chessproblem, image_pixel_size)
            image.save('%s_%d.png' % (filename_prefix, index))
        except Exception as e:
            print('ERROR during PNG generation: %r' % e)

if args.filename != None:
    memory_db_service = create_memory_db(cpe_config.config_dir)
    parser = ChessProblemLatexParser(cpe_config, memory_db_service)
    image_pixel_size = int(args.pixel_size)
    if image_pixel_size not in [32, 36, 40, 44, 48]:
        raise Exception('Invalid image pixel size spezified.')
    document = None
    with open(args.filename, 'r') as f:
        document = parser.parse_latex_str(f.read())
    if document != None:
        generate_png_files(document, image_pixel_size, args.filename)
else:
    parser.print_help()

