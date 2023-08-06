#!/usr/bin/env python3

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
from chessproblem.config import create_config

parser = ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-d', '--database', dest='database_url', default=None,
        help='the url of the database to lookup countries and cities')
parser.add_argument('-c', '--config_dir', dest='config_dir',
        help='specifies the configuration directory', default=None)

args = parser.parse_args()

if args.config_dir != None:
    cpe_config = create_config(args.config_dir)
else:
    cpe_config = create_config()


from chessproblem.io import ChessProblemLatexParser
from chessproblem.model.db import DbService, InconsistentData
from chessproblem.model.memory_db import create_memory_db

import chessproblem.model as model

def read_authors(filename):
    parser = ChessProblemLatexParser(cpe_config, create_memory_db(cpe_config.config_dir))
    with open(filename) as f:
        document = parser.parse_latex_str(f.read())
    result = []
    for index in range(document.get_problem_count()):
        problem = document.get_problem(index)
        for author in problem.authors:
            result.append(author)
    return result

def city_name(city):
    if city != None:
        return city.name
    else:
        return ''

def check_authors(authors, db_service):
    for author in authors:
        print(str(author))
        db_author = db_service.find_author_by_lastname_firstname(author.lastname, author.firstname)
        if author.city != None:
            db_city = db_service.find_city_by_name(author.city.name)
            if db_city != None:
                if author.city.name != db_city.name:
                    print('-    name of city in file [' + author.city.name + '] written different than in db: ' + db_city.name)
            else:
                print('-    city not known: ' + author.city.name)
            if author.city.country != None:
                db_country = db_service.find_country_by_code(author.city.country.car_code)
                if db_country != None:
                    if author.city.country.car_code != db_country.code():
                        print('-    country code [' + author.city.country.car_code + '] different than default code for country: ' + db_country.code())
                else:
                    print('-    country code [' + author.city.country.car_code + '] unknown.')

            else:
                db_country = None
        else:
            db_city = None
            db_country = None
        if db_author != None:
            if author.lastname != db_author.lastname:
                print('-    lastname of author [' + author.lastname + '] written different than in db: ' + db_author.lastname)
            if author.firstname != db_author.firstname:
                print('-    firstname of author [' + author.firstname + '] written different than in db: ' + db_author.firstname)
            if db_author.city != db_city:
                print('-    city stored for author in db [' + city_name(db_author.city) + '] different city found in db: ' + city_name(db_city))
        else:
            print('-    Author not found')

if args.filename != None:
    if args.database_url != None:
        database_url = args.database_url
    else:
        database_url = cpe_config.database_url
    db_service = DbService(database_url)
    authors = read_authors(args.filename)
    check_authors(authors, db_service)
else:
    parser.print_help()

