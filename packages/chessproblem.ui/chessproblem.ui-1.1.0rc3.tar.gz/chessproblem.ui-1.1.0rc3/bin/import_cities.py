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
import chessproblem.config as config
from chessproblem.model.memory_db import create_memory_db

usage = '''
%prog [options] filename

This script extracts cities from the given TeX file containing chess problem.
The default behaviour is to print a list of cities found inside the diagrams using
the CSV file (separator is ;) format:
-   car_code
-   name
-   this column will give you a hint about problems, which should be fixed before importing this file.
'''
parser = ArgumentParser(usage=usage)
parser.add_argument('filename')
parser.add_argument('-d', '--database', dest='database_url', default=None,
        help='the url of the database to lookup countries and cities')
parser.add_argument('-i', '--import', dest='check', action='store_false', default=True,
        help='import the cities found in the file into the database instead of listing the cities')
parser.add_argument('-c', '--config_dir', dest='config_dir', help='specifies the configuration directory', default=None)

args = option_parser.parse_args()

if args.config_dir != None:
    cpe_config = config.create_config(args.config_dir)
else:
    cpe_config = config.create_config()

from chessproblem.io import ChessProblemLatexParser
from chessproblem.model.db import DbService, InconsistentData

import chessproblem.model as model

def extract_cities(filename, cpe_config, memory_db_service):
    parser = ChessProblemLatexParser()
    with open(filename) as f:
        document = parser.parse_latex_str(f.read())
    result = []
    for index in range(document.get_problem_count()):
        problem = document.get_problem(index)
        for author in problem.authors:
            if author.city != None:
                result.append(author.city)
    return result
            
def display_cities(cities, db_service):
    for city in cities:
        country_code = city.country.car_code
        country = db_service.find_country_by_code(country_code)
        country_message = ''
        if country != None:
            if country.car_code != None and country.car_code != country_code:
                country_message = 'Please use the car_code ' + country.car_code + ' as country_code.'
        else:
            country_message = 'Country code ' + country_code + ' not found.'
        print(country_code + ';' + city.name + ';' + country_message)

def import_cities(cities, db_service):
    for city in cities:
        country_code = city.country.car_code
        country = db_service.find_country_by_code(country_code)
        city.country = country
        try:
            stored_city = db_service.find_city_by_name_and_country(city.name, country)
            if stored_city == None:
                print('importing city: ' + str(city))
                db_service.store_city(city)
            else:
                print('city already available: ' + str(city))
        except InconsistentData as e:
            print(e)

if args.filename != None:
    if args.database_url != None:
        database_url = cpe_config.database_url
    else:
        database_url = args.database_url
    db_service = DbService(database_url)
    memory_db_service = create_memory_db(cpe_config.config_dir)
    cities = extract_cities(args.filename, cpe_config, memory_db_service)
    if options.check:
        display_cities(cities, db_service)
    else:
        import_cities(cities, db_service)
else:
    option_parser.print_help()

