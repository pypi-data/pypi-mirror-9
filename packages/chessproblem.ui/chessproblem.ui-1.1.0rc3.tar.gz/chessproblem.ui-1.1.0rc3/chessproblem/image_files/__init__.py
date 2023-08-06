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
This module encapsulates the resultion from chess pieces indexes to image filenames.
'''
import os.path

from gi.repository import Gtk, GdkPixbuf
from cairo import ImageSurface

PIECE_TYPE_OFFSETS = [0, 1, 2, 3, 4, 5, 180, 145]
PIECE_COLOR_OFFSETS = [0, 12, 6]
PIECE_ROTATION_OFFSETS = [0, 36, 72, 108]


def get_image_directory(image_pixel_size):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'images',str(image_pixel_size))


import logging

LOGGER = logging.getLogger('chessproblem.image_files')


def get_image_filename(index, image_pixel_size):
    '''
    Calculates the name of an image file for a given image index.
    '''
    image_file_name = os.path.join(get_image_directory(image_pixel_size), str(index)+'.xbm')
    return image_file_name

def get_png_filename(index, image_pixel_size):
    '''
    Calculates the name of an image file for a given image index.
    '''
    image_file_name = os.path.join(get_image_directory(image_pixel_size), str(index)+'.png')
    return image_file_name

def image_offset(piece_type, piece_color, piece_rotation):
    '''
    Calculates the image offset for the given combination of 'piece_type', 'piece_color' and 'piece_rotation'.
    '''
    return PIECE_TYPE_OFFSETS[piece_type] + PIECE_COLOR_OFFSETS[piece_color] + PIECE_ROTATION_OFFSETS[piece_rotation]

def create_chessimage_pixbuf(image_index, image_pixel_size):
    '''
    Get the chessimage Gtk.Pixbuf for the given index.
    '''
    filename = get_png_filename(image_index,  image_pixel_size)
    LOGGER.debug('Loading image file: %s' % filename)
    result = GdkPixbuf.Pixbuf.new_from_file(filename)
    return result

def create_chessimage_surface(image_index, image_pixel_size):
    '''
    Get the chessimage cairo.ImageSurface
    '''
    filename = get_png_filename(image_index,  image_pixel_size)
    LOGGER.debug('Loading image surface from file: %s' % filename)
    result = ImageSurface.create_from_png(filename)
    return result

