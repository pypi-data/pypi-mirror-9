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
This module contains e.g. factory methods for widgets.
'''

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

def create_button(label, handler, show=True, data=None):
    '''
    Creates  a button with the given label and connects the given handler.
    label:
        the label of the button
    handler:
        the handler, which is called, when the button is pressed
    show:
        whether the button should be initially visible
    data:
        additional data, which is provided when calling the handler method
    returns the created button
    '''
    result = Gtk.Button(label)
    result.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#c4c2bd'))
    result.connect('clicked', handler, data)
    if show:
        result.show()
    return result

def to_model(entry_text):
    if entry_text == '':
        return None
    else:
        return entry_text

def to_entry(model_text):
    if model_text == None:
        return ''
    else:
        return model_text

