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


import os
from os.path import realpath, dirname, join, exists, expanduser

import re

import shutil

import logging.config

DEFAULT_LOGGING_CONFIG='''
[loggers]
keys=root,chessproblem,sqlalchemy

[handlers]
keys=fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=fileHandler

[logger_sqlalchemy]
qualname=sqlalchemy
handlers=
level=INFO

[logger_chessproblem]
qualname=chessproblem
handlers=
level=DEBUG

[handler_fileHandler]
class=handlers.RotatingFileHandler
formatter=simpleFormatter
args=('{0}', 'a', 1048576, 10)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=
'''

def default_city_split(city):
    '''
    This is used to split the city string from a latex input into the abbreviation for country and the city itself.

    The country abbreviation may consist of 1 to 3 uppercase letters followed by 1 to 3 dashes.
    '''
    m = re.match('([A-Z]{1,3})-{1,3}(.+)', city)
    if m != None:
        return [m.group(1), m.group(2)]
    else:
        return [city]

class CpeConfig(object):
    '''
    Provides the configuration data for the Chessproblem-Editor application.
    '''
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.city_split = default_city_split
        self.default_country = 'D'
        self.image_pixel_size = 40
        self.legend_display = 'always'
        self.database_url = 'sqlite:///' + join(self.config_dir, 'cpe.db')
        self.compile_menu_actions = []
        self.latex_compiler = None
        self.compiled_latex_viewer = None
        self.popeye_executable = None
        self.popeye_directory = join(config_dir, 'popeye')
        self.computer_tested = '+'
        self.png_pixel_size = 40

def create_config(config_dir=None):
    # if no configuration directory is specified, we will use our default
    if config_dir == None:
        config_dir = join(expanduser('~'), '.cpe')
    # if the configuration directory does not exist, we will create it
    if not exists(config_dir):
        os.mkdir(config_dir)
    # configure logging
    log_directory = join(config_dir, 'log')
    logging_config_file=join(config_dir, 'logging.config')
    if not exists(logging_config_file):
        os.mkdir(log_directory)
        import platform
        log_filename = join(log_directory, 'cpe.log')
        if platform.system() == 'Windows':
            # When the logging system reads the configuration file, a single backslash is
            # interpreted to introduce a special character
            log_filename = log_filename.replace('\\', '\\\\')
        with open(logging_config_file, 'w') as f:
            f.write(DEFAULT_LOGGING_CONFIG.format(log_filename))
    # Use the logging configuration
    logging.config.fileConfig(logging_config_file)
    # Create the CPE configuration object
    result = CpeConfig(config_dir)
    # Adjust the configuration using the 'user configuration file'.
    user_config = join(config_dir, 'config.py')
    config_template_filename = join(dirname(realpath(__file__)), 'config_template.py')
    if not exists(user_config):
        shutil.copy(config_template_filename, user_config)
    exec(compile(open(user_config).read(), user_config, 'exec'), {'DEFAULT_CONFIG': result})
    return result


