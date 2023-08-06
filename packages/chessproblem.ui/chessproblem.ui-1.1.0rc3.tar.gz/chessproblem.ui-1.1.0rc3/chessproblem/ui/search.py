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
This module contains generic user interface elements for searching.
'''

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GObject

import logging

LOGGER = logging.getLogger('chessproblem.ui.search')

from .ui_common import to_entry

class AbstractDataListBox(Gtk.TreeView):
    def __init__(self, data_provider, selection_handler):
        Gtk.TreeView.__init__(self)
        self.data_provider = data_provider
        self.selection_handler = selection_handler
        self.liststore = self.data_provider.create_liststore()
        self.set_model(self.liststore)
        self.set_size_request(200, 200)
        column_headings = self.data_provider.column_headings()
        for index in range(len(column_headings)):
            column_heading = column_headings[index]
            self.append_column(Gtk.TreeViewColumn(column_heading, Gtk.CellRendererText(), text=index))
        self.objects = []
        self.get_selection().connect('changed', self._on_selection_changed)
        
    def _on_selection_changed(self, treeview):
        model, it = self.get_selection().get_selected()
        if it != None:
            selected_index = int(model.get_string_from_iter(it))
            selected_object = self.objects[selected_index]
            self.selection_handler(selected_object)
        else:
            self.selection_handler(None)

    def set_objects(self, objects):
        self.objects = objects
        self._on_objects_changed()

    def _on_objects_changed(self):
        self.liststore.clear()
        for o in self.objects:
            self.liststore.append(self.data_provider.create_liststore_data(o))

    def selection_updated(self):
        model, it = self.get_selection().get_selected()
        if it != None:
            selected_index = int(model.get_string_from_iter(it))
            data = self.data_provider.create_liststore_data(self.objects[selected_index])
            for index in range(len(data)):
                value = to_entry(data[index])
                self.liststore.set_value(it, index, value)

    def remove_selected(self):
        model, it = self.get_selection().get_selected()
        if it != None:
            selected_index = int(model.get_string_from_iter(it))
            del self.objects[selected_index]
            self.liststore.remove(it)

    def status_message(self):
        return self.data_provider.status_message(len(self.objects))

class SearchListBox(AbstractDataListBox):
    def __init__(self, data_provider, search_handler, selection_handler):
        AbstractDataListBox.__init__(self, data_provider, selection_handler)
        self.search_handler = search_handler
        self.set_filter('')

    def set_filter(self, expr):
        objects = self.search_handler(expr)
        LOGGER.debug('SearchListBox.set_filter(' + expr + '): got ' + str(len(objects)) + ' objects.')
        self.set_objects(objects)

class SearchPanel(Gtk.VBox):
    def __init__(self, search_data_provider, selection_handler):
        Gtk.VBox.__init__(self)
        self.table_layout = Gtk.Grid()
        self.table_layout.set_column_spacing(8)
        self.table_layout.set_row_spacing(8)
        self.table_layout.set_row_homogeneous(True)
        self.table_layout.show()
        self.pack_start(self.table_layout, True, True, 10)
        self.label = Gtk.Label(label='search/filter')
        self.label.show()
        self.table_layout.attach(self.label, 0, 0, 1, 1)
        self.entry_search = Gtk.Entry()
        self.entry_search.connect('changed', self._on_entry_search_changed)
        self.entry_search.show()
        self.table_layout.attach(self.entry_search, 1, 0, 1, 1)
        self.listbox = SearchListBox(search_data_provider, search_data_provider.filtered_objects, selection_handler)
        self.listbox.show()
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.add(self.listbox)
        self.scrolledwindow.show()
        self.table_layout.attach(self.scrolledwindow, 0, 1, 2, 5)
        self._filter_listeners = []

    def _on_entry_search_changed(self, widget, data=None):
        self.run_filter()

    def add_filter_listener(self, filter_listener):
        self._filter_listeners.append(filter_listener)

    def run_filter(self):
        LOGGER.debug('SearchPanel._on_entry_changed(...) ' + self.entry_search.get_text())
        self.listbox.set_filter(self.entry_search.get_text())
        for filter_listener in self._filter_listeners:
            filter_listener()

    def selection_updated(self):
        self.listbox.selection_updated()

    def enable_panel(self, enable=True):
        self.entry_search.set_sensitive(enable)
        self.listbox.set_sensitive(enable)

    def status_message(self):
        return self.listbox.status_message()
        

class AbstractSearchDialog(Gtk.Dialog):
    def __init__(self, title, search_data_provider, selection_handler):
        Gtk.Dialog.__init__(self)
        self.set_title(title)
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.set_response_sensitive(Gtk.ResponseType.ACCEPT, False)
        self.search_panel = SearchPanel(search_data_provider, selection_handler)
        self.search_panel.show()
        self.get_content_area().pack_start(self.search_panel, True, True, 0)


