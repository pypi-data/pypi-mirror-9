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
This module contains special gtk user interface elements used to display chess problem information.
'''
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GObject

from io import StringIO

from chessproblem.ui.search import SearchPanel, AbstractDataListBox, AbstractSearchDialog

from chessproblem.ui.search_descriptors import AuthorSearchDataProvider, SourceSearchDataProvider, ConditionSearchDataProvider

from chessproblem.ui.ui_common import create_button

from chessproblem.model import PIECE_ROTATION_NORMAL, PieceDef

from chessproblem.model.conditions import Condition
from chessproblem.model.piecetypes import PieceType

from chessproblem.image_files import image_offset, create_chessimage_pixbuf
from chessproblem.io import piece_color, piece_type, piece_rotation, PIECE_CHARACTERS, PIECE_COLORS, PIECE_ROTATIONS
from chessproblem.io import write_array_member_data, parse_gridlines, parse_fieldtext, fieldtext_tostr

import logging

LOGGER = logging.getLogger('chessproblem.ui.display')

LABEL_PADDING=4

_ENTRIES = ['specialdiagnum', 'sourcenr', 'source', 'issue', 'day', 'month', 'year', 'dedication', 'after', 'version', 'label', 'award', 'tournament', 'stipulation', 'remark']

_MULTILINE = ['solution', 'comment']
_TEXTLISTS = {
        'gridlines': None,
        'fieldtext': fieldtext_tostr }

_TEXTVIEWS = []

_CHECKBOXES = ['gridchess', 'verticalcylinder', 'horizontalcylinder', 'allwhite', 'switchcolors']

def _non_none_str(value):
    if value != None:
        return value
    else:
        return ''

def _to_single_line(value):
    if value == None:
        return ''
    else:
        lines = value.splitlines()
        if len(lines) == 1:
            return lines[0]
        else:
            return lines[0] + ' \u21b5'

def _do_nothing():
    pass

class SourceSearchDialog(AbstractSearchDialog):
    '''
    A dialog to search for sources.
    '''
    def __init__(self, db_service):
        AbstractSearchDialog.__init__(self, 'Source search', SourceSearchDataProvider(db_service), self.object_selected)
        self.result = None

    def object_selected(self, source):
        self.set_response_sensitive(Gtk.ResponseType.ACCEPT, source != None)
        self.result = source

class InfoArea(Gtk.Grid):
    def __init__(self, cpe_config, db_service, memory_db_service, visual_change_listener):
        Gtk.Grid.__init__(self)
        self.visual_change_listener = visual_change_listener
        self.set_column_homogeneous(False)
        self.set_row_homogeneous(True)
        self.cpe_config = cpe_config
        self.db_service = db_service
        self.memory_db_service = memory_db_service
        row = 0
        self._create_and_attach_labelled_entry('specialdiagnum', 0, row, char_width=10)
        self._create_and_attach_labelled_entry('sourcenr', 2, row, char_width=8)
        self.button_select_source = create_button('source', self._on_select_source)
        self._attach_button(self.button_select_source, 4, row)
        self._create_and_attach_entry('source', 5, row, width=4)
        row += 1
        self._create_and_attach_labelled_entry('issue', 0, row, char_width=10)
        self._create_and_attach_labelled_entry('day', 2, row, char_width=2)
        self._create_and_attach_labelled_entry('month', 4, row, char_width=5)
        self._create_and_attach_labelled_entry('year', 6, row, char_width=4)
        row += 1
        self._create_and_attach_label('authors', 0, row)
        self.button_edit_authors = create_button('edit', self._on_edit_authors)
        self._attach_button(self.button_edit_authors, 0, row + 1)
        self.liststore_authors = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING)
        self.listbox_authors = Gtk.TreeView(self.liststore_authors)
        self.listbox_authors.append_column(Gtk.TreeViewColumn('lastname', Gtk.CellRendererText(), text=0))
        self.listbox_authors.append_column(Gtk.TreeViewColumn('givenname', Gtk.CellRendererText(), text=1))
        self.listbox_authors.append_column(Gtk.TreeViewColumn('city', Gtk.CellRendererText(), text=2))
        self.listbox_authors.set_size_request(-1, 100)
        self.listbox_authors.show()
        self._attach_listbox(self.listbox_authors, 1, row)
        row += 3
        self._create_and_attach_labelled_entry('dedication', 0, row, width=3)
        self._create_and_attach_labelled_entry('after', 4, row, width=3)
        row += 1
        self._create_and_attach_labelled_entry('version', 0, row, width=3)
        self._create_and_attach_labelled_entry('label', 4, row, width=3)
        row += 1
        self._create_and_attach_labelled_entry('award', 0, row, char_width=10)
        self._create_and_attach_labelled_entry('tournament', 2, row, width=5)
        row += 1
        self._create_and_attach_labelled_entry('stipulation', 0, row, width=2)
        self._create_and_attach_labelled_entry('remark', 3, row, width=4)
        row += 1
        self._create_and_attach_label('conditions', 0, row)
        self.button_edit_conditions = create_button('edit', self._on_edit_conditions)
        self._attach_button(self.button_edit_conditions, 0, row + 1)
        self.liststore_conditions = Gtk.ListStore(GObject.TYPE_STRING)
        self.listbox_conditions = Gtk.TreeView(self.liststore_conditions)
        self.listbox_conditions.append_column(Gtk.TreeViewColumn('condition', Gtk.CellRendererText(), text=0))
        self.listbox_conditions.set_size_request(-1, 80)
        self.listbox_conditions.show()
        self._attach_listbox(self.listbox_conditions, 1, row, width=3)
        # twins
        self._create_multi_string('twins', 'twin', 4, row, 3)
        row += 3
        self._create_and_attach_label('piecedefs', 0, row)
        self.button_edit_piecedefs = create_button('edit', self._on_edit_piecedefs)
        self._attach_button(self.button_edit_piecedefs, 0, row + 1)
        self.listbox_piecedefs = PiecedefsListBox(self.cpe_config.image_pixel_size)
        self.listbox_piecedefs.set_size_request(-1, 80)
        self.listbox_piecedefs.show()
        self._attach_listbox(self.listbox_piecedefs, 1, row, width=3)
        self._create_multi_string('themes', 'theme', 4, row, 3)
        row += 3
        self._create_textview('solution', row)
        row += 1
        self._create_textview('comment', row)
        row += 1
        self._create_textview('gridlines', row, value_prefix='textlist_', button_handler=self._on_edit_gridlines)
        row += 1
        self._create_textview('fieldtext', row, value_prefix='textlist_', button_handler=self._on_edit_fieldtext)
        row += 1

    def save_to_problem(self):
        '''
        Transfers the value of all text fields to the current problem.
        '''
        for name in _ENTRIES:
            entry = getattr(self, 'entry_' + name)
            value = entry.get_text()
            if value == '':
                setattr(self._problem, name, None)
            else:
                setattr(self._problem, name, value)
        for name in _MULTILINE:
            value = getattr(self, 'multiline_' + name)
            if value == '':
                setattr(self._problem, name, None)
            else:
                setattr(self._problem, name, value)
        for name in _TEXTVIEWS:
            entry = getattr(self, 'textview_' + name)
            textbuffer = entry.get_buffer()
            value = textbuffer.get_property('text')
            if value == '':
                setattr(self._problem, name, None)
            else:
                setattr(self._problem, name, value)


    def set_problem(self, problem):
        '''
        Registers the given problem and transfers its data to the widgets.
        '''
        self._problem = problem
        # Show all normal text values
        for name in _ENTRIES:
            value = getattr(problem, name)
            entry = getattr(self, 'entry_' + name)
            entry.set_text(_non_none_str(value))
        for name in _MULTILINE:
            value = getattr(problem, name)
            setattr(self, 'multiline_' + name, value)
            entry = getattr(self, 'entry_' + name)
            entry.set_text(_to_single_line(value))
        for name in _TEXTVIEWS:
            value = getattr(problem, name)
            textview = getattr(self, 'textview_' + name)
            textbuffer = textview.get_buffer()
            if value != None:
                textbuffer.set_text(value)
            else:
                textbuffer.set_text('')
        for name in _TEXTLISTS.keys():
            array = getattr(problem, name)
            setattr(self, 'textlist_' + name, array)
            entry = getattr(self, 'entry_' + name)
            if len(array) > 0:
                output = StringIO()
                write_array_member_data(output, array, separator=', ', member_tostr=_TEXTLISTS[name])
                entry.set_text(_to_single_line(output.getvalue()))
            else:
                entry.set_text('')
        self._fill_authors_liststore()
        self._fill_conditions_liststore()
        self._fill_multistring_liststore('twins')
        self._fill_multistring_liststore('themes')
        self._fill_piecedefs_liststore()

    def _fill_conditions_liststore(self):
        self.liststore_conditions.clear()
        for condition in self._problem.condition:
            self.liststore_conditions.append([condition.get_name()])


    def _fill_multistring_liststore(self, name):
        liststore = getattr(self, 'liststore_' + name)
        liststore.clear()
        values = getattr(self._problem, name)
        for value in values:
            liststore.append([value])

    def _fill_authors_liststore(self):
        self.liststore_authors.clear()
        for author in self._problem.authors:
            self.liststore_authors.append([author.lastname, author.firstname, str(author.city)])

    def _fill_piecedefs_liststore(self):
        self.listbox_piecedefs.set_piecedefs(self._problem.piecedefs)

    def _create_and_attach_label(self, name, x, y):
        label = self._create_label(name)
        self.attach(label, x, y, 1, 1)

    def _create_label(self, name):
        label = Gtk.Label(label=name)
        setattr(self, 'label_' + name, label)
        label.show()
        return label

    def _create_textview(self, fieldname, row, value_prefix='multiline_', button_handler=None):
        '''
        Creates a 'readonly' entry and a button which - when pressed - opens a
        separate dialog to edit the text for the given 'fieldname'.
        '''
        if button_handler != None:
            _button = create_button(fieldname, button_handler, data=fieldname)
        else:
            _button = create_button(fieldname, self._on_edit_multiline, data=fieldname)
        setattr(self, 'button_edit_' + fieldname, _button)
        self._attach_button(_button, 0, row)
        _entry = self._create_and_attach_entry(fieldname, 1, row, width=7)
        _entry.set_property('editable', False)
        setattr(self, value_prefix + fieldname, None)

    def _create_multi_string(self, name, singular, x, y, width):
        self._create_and_attach_label(name, x, y)
        _button = create_button('edit', self._on_edit_multistring, data=[name, singular])
        setattr(self, 'button_edit_' + name, _button)
        self._attach_button(_button, x, y + 1)
        _liststore = Gtk.ListStore(GObject.TYPE_STRING)
        setattr(self, 'liststore_' + name, _liststore)
        _listbox = Gtk.TreeView(_liststore)
        setattr(self, 'listbox_' + name, _listbox)
        _listbox.append_column(Gtk.TreeViewColumn(singular, Gtk.CellRendererText(), text=0))
        _listbox.set_size_request(-1, 80)
        _listbox.show()
        self._attach_listbox(_listbox, x + 1, y, width=width)

    def _attach_button(self, button, x,  y):
        self.attach(button, x, y, 1, 1)

    def _create_and_attach_labelled_entry(self, name, x, y, char_width=None, width=1):
        '''
        Creates a label with the given name prefixed by 'label_' and an entry with the given name prefixed by 'entry_'.
        The label is attached at position x, y; the entry is attached at position x + 1, y.
        '''
        self._create_and_attach_label(name, x, y)
        self._create_and_attach_entry(name, x + 1, y, char_width, width)

    def _create_and_attach_entry(self, name, x, y, char_width=None, width=1):
        entry = Gtk.Entry()
        setattr(self, 'entry_' + name, entry)
        entry.show()
        if char_width != None:
            entry.set_width_chars(char_width)
        self.attach(entry, x, y, width, 1)
        return entry

    def _attach_entry(self, entry, x, y, width=1):
        self.attach(entry, x, y, width, 1)

    def _attach_listbox(self, listbox, x, y, width=7, height=3):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(listbox)
        scrolled_window.show()
        self.attach(scrolled_window, x, y, width, height)

    def _on_select_source(self, widget, data=None):
        search_dialog = SourceSearchDialog(self.db_service)
        response = search_dialog.run()
        search_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            source = search_dialog.result
            self.entry_source.set_text(source.name)

    def _on_edit_authors(self, widget, data=None):
        '''
        Called when the 'edit' button for authors is pressed.
        '''
        _edit_authors_dialog = EditAuthorsDialog(self.db_service, self._problem.authors)
        response = _edit_authors_dialog.run()
        _edit_authors_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            self._problem.authors = _edit_authors_dialog.get_values()
            self._problem.cities = [author.city for author in self._problem.authors]
            self._fill_authors_liststore()

    def _on_edit_conditions(self, widget, data=None):
        '''
        Called when the 'edit' button for conditions is pressed.
        '''
        _edit_conditions_dialog = EditConditionsDialog(self.memory_db_service, self._problem.condition)
        response = _edit_conditions_dialog.run()
        _edit_conditions_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            self._problem.condition = _edit_conditions_dialog.get_values()
            self._fill_conditions_liststore()

    def _on_edit_multistring(self, widget, data):
        '''
        Called when the 'edit' button for twins is pressed.
        '''
        name = data[0]
        singular = data[1]
        values = getattr(self._problem, name)
        _edit_dialog = EditStringListDialog(values, name, singular)
        response = _edit_dialog.run()
        _edit_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            setattr(self._problem, name, _edit_dialog.get_values())
            self._fill_multistring_liststore(name)

    def _on_edit_piecedefs(self, widget, data=None):
        _edit_piecedefs_dialog = EditPiecedefsDialog(self._problem, self.memory_db_service, self.cpe_config.image_pixel_size)
        response = _edit_piecedefs_dialog.run()
        _edit_piecedefs_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            piecedefs = _edit_piecedefs_dialog.get_piecedefs()
            self._problem.piecedefs = piecedefs
            self.listbox_piecedefs.set_piecedefs(piecedefs)

    def _on_edit_multiline(self, widget, data=None):
        '''
        Called when one of the multiline buttons is pressed
        '''
        current_entry = getattr(self, 'entry_' + data)
        current_text = getattr(self, 'multiline_' + data)
        _edit_multiline_dialog = EditMultilineTextDialog(
                data, current_text)
        response = _edit_multiline_dialog.run()
        _edit_multiline_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            new_text = _edit_multiline_dialog.get_text()
            setattr(self, 'multiline_' + data, new_text)
            current_entry.set_text(_to_single_line(new_text))

    def _on_edit_gridlines(self, widget, data=None):
        '''
        Called when the 'gridlines' button is pressed
        '''
        current_entry = getattr(self, 'entry_' + data)
        current_data = getattr(self, 'textlist_' + data)
        text = StringIO()
        write_array_member_data(text, current_data, separator=', ')
        _edit_multiline_dialog = EditMultilineTextDialog(
                data, text.getvalue())
        response = _edit_multiline_dialog.run()
        _edit_multiline_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            new_text = _edit_multiline_dialog.get_text()
            gridlines = parse_gridlines(new_text)
            setattr(self, 'textlist_' + data, gridlines)
            current_entry.set_text(_to_single_line(new_text))
            setattr(self._problem, 'gridlines', gridlines)
            self.visual_change_listener()

    def _on_edit_fieldtext(self, widget, data=None):
        '''
        Called when the 'gridlines' button is pressed
        '''
        current_entry = getattr(self, 'entry_' + data)
        current_data = getattr(self, 'textlist_' + data)
        text = StringIO()
        write_array_member_data(text, current_data, separator=', ', member_tostr=fieldtext_tostr)
        _edit_multiline_dialog = EditMultilineTextDialog(
                data, text.getvalue())
        response = _edit_multiline_dialog.run()
        _edit_multiline_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            new_text = _edit_multiline_dialog.get_text()
            fieldtext = parse_fieldtext(new_text)
            setattr(self, 'textlist_' + data, fieldtext)
            current_entry.set_text(_to_single_line(new_text))
            setattr(self._problem, 'fieldtext', fieldtext)
            self.visual_change_listener()


class CheckBoxArea(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.set_column_homogeneous(True)
        self.set_row_homogeneous(True)
        self.show()
        self.visual_change_listener = _do_nothing
        self._create_and_attach_checkbox('gridchess', 0, 0)
        self._create_and_attach_checkbox('verticalcylinder', 1, 0)
        self._create_and_attach_checkbox('horizontalcylinder', 2, 0)
        self._create_and_attach_checkbox('allwhite', 0, 1)
        self._create_and_attach_checkbox('switchcolors', 1, 1)

    def _create_and_attach_checkbox(self, name, x, y):
        '''
        Creates a checkbox with the given name suffix and attaches this checkbox at position x, y.
        Additionally the 'toggled' event is registered to the _on_checkbox method.
        '''
        checkbox = Gtk.CheckButton(name)
        setattr(self, 'checkbox_' + name, checkbox)
        checkbox.show()
        checkbox.connect('toggled', self._on_checkbox, name)
        self.attach(checkbox, x, y, 1, 1)

    def save_to_problem(self):
        for name in _CHECKBOXES:
            self.save_checkbox_to_problem(name)

    def save_checkbox_to_problem(self, name):
        '''
        Stores the value of the checkbox with the given name to the problem.
        '''
        checkbox = getattr(self, 'checkbox_' + name)
        setattr(self._problem, name, checkbox.get_active())

    def set_problem(self, problem):
        '''
        Registers the given problem and transfers its data to the widgets.
        '''
        self._problem = problem
        for name in _CHECKBOXES:
            checkbox = getattr(self, 'checkbox_' + name)
            value = getattr(self._problem, name)
            checkbox.set_active(value)

    def set_visual_change_listener(self, listener):
        self.visual_change_listener = listener

    def _on_checkbox(self, widget, data=None):
        self.save_checkbox_to_problem(data)
        if data == 'allwhite':
            self.checkbox_switchcolors.set_sensitive(not self._problem.allwhite)
        if data == 'switchcolors':
            self.checkbox_allwhite.set_sensitive(not self._problem.switchcolors)
        self.visual_change_listener()

class ConditionsListBox(AbstractDataListBox):
    def __init__(self, db_service, selection_handler):
        AbstractDataListBox.__init__(self, ConditionSearchDataProvider(db_service), selection_handler)

    def add_condition(self, condition):
        self.objects.append(condition)
        self._on_objects_changed()


class EditConditionsDialog(Gtk.Dialog):
    '''
    This dialog allows select conditions from a list of available conditions.
    The list of selected conditions is displayed on the right side of the dialog.
    The list of available conditions is displayed on the left side of the dialog.
    '''
    def __init__(self, db_service, conditions):
        Gtk.Dialog.__init__(self)
        self.set_title('edit conditions')
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.db_service = db_service
        self.table_layout = Gtk.Grid()
        self.table_layout.show()
        self.table_layout.set_column_spacing(8)
        self.table_layout.set_column_homogeneous(True)
        self.get_content_area().pack_start(self.table_layout, True, True, 0)
        self.box_selected_conditions = Gtk.VBox(False, 0)
        self.box_selected_conditions.show()
        self.table_layout.attach(self.box_selected_conditions, 0, 0, 2, 3)
        self.label_selected_conditions = Gtk.Label(label='selected conditions')
        self.label_selected_conditions.show()
        self.box_selected_conditions.pack_start(self.label_selected_conditions, False, False, 0)
        self.listbox_selected_conditions = ConditionsListBox(db_service, self._on_selected_conditions_changed)
        self.listbox_selected_conditions.set_objects(conditions)
        self.listbox_selected_conditions.show()
        self.scrolledwindow_selected_conditions = Gtk.ScrolledWindow()
        self.scrolledwindow_selected_conditions.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow_selected_conditions.add(self.listbox_selected_conditions)
        self.scrolledwindow_selected_conditions.show()
        self.box_selected_conditions.pack_start(self.scrolledwindow_selected_conditions, True, True, 0)
        self.button_box = Gtk.VBox(False, 0)
        self.button_box.show()
        self.table_layout.attach(self.button_box, 2, 1, 1, 1)
        self.button_add_condition = Gtk.Button('add condition')
        self.button_add_condition.set_sensitive(False)
        self.button_add_condition.connect('clicked', self._on_button_add_condition)
        self.button_add_condition.show()
        self.button_box.pack_start(self.button_add_condition, False, False, 5)
        self.button_remove_condition = Gtk.Button('remove condition')
        self.button_remove_condition.set_sensitive(False)
        self.button_remove_condition.connect('clicked', self._on_button_remove_condition)
        self.button_remove_condition.show()
        self.button_box.pack_start(self.button_remove_condition, False, False, 5)
        self.button_add_other_condition = Gtk.Button('add other condition')
        self.button_add_other_condition.set_sensitive(True)
        self.button_add_other_condition.connect('clicked', self._on_button_add_other_condition)
        self.button_add_other_condition.show()
        self.button_box.pack_end(self.button_add_other_condition, False, False, 5)
        self.conditions_search_panel = SearchPanel(ConditionSearchDataProvider(self.db_service), self._on_search_condition_selected)
        self.conditions_search_panel.show()
        self.table_layout.attach(self.conditions_search_panel, 3, 0, 2, 3)

    def _on_search_condition_selected(self, condition):
        self.selected_search_condition = condition
        self.button_add_condition.set_sensitive(condition != None)

    def _on_selected_conditions_changed(self, condition):
        self.button_remove_condition.set_sensitive(condition != None)

    def _on_button_add_condition(self, widget, data=None):
        if self.selected_search_condition != None:
            self.listbox_selected_conditions.add_condition(self.selected_search_condition)

    def _on_button_remove_condition(self, widget, data=None):
        self.listbox_selected_conditions.remove_selected()

    def _on_button_add_other_condition(self, widget, data=None):
        _edit_other_condition_dialog = EditOtherConditionDialog()
        response = _edit_other_condition_dialog.run()
        _edit_other_condition_dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            condition_text = _edit_other_condition_dialog.get_contition_text()
            condition = Condition(condition_text)
            self.listbox_selected_conditions.add_condition(condition)
    
    def get_values(self):
        return self.listbox_selected_conditions.objects

class EditOtherConditionDialog(Gtk.Dialog):
    '''
    Used to edit conditions, which are no standard conditions or need additional parameters.
    '''
    def __init__(self):
        Gtk.Dialog.__init__(self,
                title='add other condition',
                flags=Gtk.DialogFlags.MODAL,
                buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        self.layout = Gtk.VBox()
        self.layout.show()
        self.get_content_area().pack_start(self.layout, True, True, 0)
        self.label_condition = Gtk.Label(label='condition')
        self.label_condition.show()
        self.layout.pack_start(self.label_condition, False, False, 5)
        self.entry_condition = Gtk.Entry()
        self.entry_condition.show()
        self.layout.pack_start(self.entry_condition, False, False, 5)

    def get_contition_text(self):
        return self.entry_condition.get_text()

class AuthorsListBox(AbstractDataListBox):
    def __init__(self, db_service, selection_handler):
        AbstractDataListBox.__init__(self, AuthorSearchDataProvider(db_service), selection_handler)

    def add_author(self, author):
        self.objects.append(author)
        self._on_objects_changed()

class EditAuthorsDialog(Gtk.Dialog):
    def __init__(self, db_service, authors):
        Gtk.Dialog.__init__(self)
        self.set_title('edit authors')
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.db_service = db_service
        self.table_layout = Gtk.Grid()
        self.table_layout.show()
        self.table_layout.set_column_spacing(8)
        self.table_layout.set_column_homogeneous(True)
        self.get_content_area().pack_start(self.table_layout, True, True, 0)
        self.box_selected_authors = Gtk.VBox(False, 0)
        self.box_selected_authors.show()
        self.table_layout.attach(self.box_selected_authors, 0, 0, 2, 3)
        self.label_selected_authors = Gtk.Label(label='selected authors')
        self.label_selected_authors.show()
        self.box_selected_authors.pack_start(self.label_selected_authors, False, False, 0)
        self.listbox_selected_authors = AuthorsListBox(db_service, self._on_selected_authors_changed)
        self.listbox_selected_authors.set_objects(authors)
        self.listbox_selected_authors.show()
        self.scrolledwindow_selected_authors = Gtk.ScrolledWindow()
        self.scrolledwindow_selected_authors.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow_selected_authors.add(self.listbox_selected_authors)
        self.scrolledwindow_selected_authors.show()
        self.box_selected_authors.pack_start(self.scrolledwindow_selected_authors, True, True, 0)
        self.button_box = Gtk.VBox(False, 0)
        self.button_box.show()
        self.table_layout.attach(self.button_box, 2, 1, 1, 1)
        self.button_add_author = Gtk.Button('add author')
        self.button_add_author.set_sensitive(False)
        self.button_add_author.connect('clicked', self._on_button_add_author)
        self.button_add_author.show()
        self.button_box.pack_start(self.button_add_author, False, False, 5)
        self.button_remove_author = Gtk.Button('remove author')
        self.button_remove_author.set_sensitive(False)
        self.button_remove_author.connect('clicked', self._on_button_remove_author)
        self.button_remove_author.show()
        self.button_box.pack_start(self.button_remove_author, False, False, 5)
        self.authors_search_panel = SearchPanel(AuthorSearchDataProvider(self.db_service), self._on_search_author_selected)
        self.authors_search_panel.show()
        self.table_layout.attach(self.authors_search_panel, 3, 0, 2, 3)

    def _on_search_author_selected(self, author):
        self.selected_search_author = author
        self.button_add_author.set_sensitive(author != None)

    def _on_selected_authors_changed(self, author):
        self.button_remove_author.set_sensitive(author != None)

    def _on_button_add_author(self, widget, data=None):
        if self.selected_search_author != None:
            self.listbox_selected_authors.add_author(self.selected_search_author)

    def _on_button_remove_author(self, widget, data=None):
        self.listbox_selected_authors.remove_selected()
    
    def get_values(self):
        return self.listbox_selected_authors.objects

class EditStringListDialog(Gtk.Dialog):
    def __init__(self, string_list, title, name):
        Gtk.Dialog.__init__(self)
        self.set_title(title)
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.table_layout = Gtk.Grid()
        self.table_layout.show()
        self.table_layout.set_row_homogeneous(True)
        self.table_layout.set_column_spacing(8)
        self.table_layout.set_row_spacing(8)
        self.get_content_area().pack_start(self.table_layout, True, True, 0)
        self.liststore_strings = Gtk.ListStore(GObject.TYPE_STRING)
        self.listbox_strings = Gtk.TreeView(self.liststore_strings)
        self.listbox_strings.set_size_request(200, 100)
        self.listbox_strings.append_column(Gtk.TreeViewColumn(name, Gtk.CellRendererText(), text=0))
        self.listbox_strings.show()
        self.table_layout.attach(self.listbox_strings, 0, 0, 1, 4)
        self.entry_string = Gtk.Entry()
        self.entry_string.show()
        self.table_layout.attach(self.entry_string, 0, 4, 1, 1)
        self.button_delete = Gtk.Button('delete ' + name)
        self.button_delete.connect('clicked', self._on_button_delete)
        self.button_delete.show()
        self.table_layout.attach(self.button_delete, 1, 1, 1, 1)
        self.button_add = Gtk.Button('add ' + name)
        self.button_add.connect('clicked', self._on_button_add)
        self.button_add.show()
        self.table_layout.attach(self.button_add, 1, 4, 1, 1)
        # Fill the liststore with the values given
        for string in string_list:
            self.liststore_strings.append([string])

    def _on_button_add(self, widget, data=None):
        value = self.entry_string.get_text()
        if value != '':
            self.liststore_strings.append([value])
            self.entry_string.set_text('')

    def _on_button_delete(self, widget, data=None):
        selection = self.listbox_strings.get_selection()
        model, it = selection.get_selected()
        if it != None:
            self.liststore_strings.remove(it)

    def get_values(self):
        result = []
        it = self.liststore_strings.get_iter_first()
        while it != None:
            value = self.liststore_strings.get_value(it, 0)
            result.append(value)
            it = self.liststore_strings.iter_next(it)
        return result


class AuthorsDisplay(Gtk.TextView):
    '''
    A spcial display to for the list of authors.
    '''

    def __init__(self):
        GObject.GObject.__init__(self)
        self.textbuffer = Gtk.TextBuffer()
        self.set_buffer(self.textbuffer)
        self.set_editable(False)

    def set_problem(self, problem):
        self.problem = problem
        self.redisplay()

    def redisplay(self):
        text = ''
        if self.problem != None:
            first = True
            for author in self.problem.authors:
                if first:
                    first = False
                else:
                    text = text + '\n'
                text = text + str(author)
        self.textbuffer.set_text(text)

class PiecedefsListBox(Gtk.TreeView):
    '''
    A listbox to display and select piecedefs of a chessproblem.
    The list has two columns. One displays the fairy chess images for the colors
    specified within a 'piecedefs' colors field; the other displays the name of
    the fairy piece.
    '''
    def __init__(self, image_pixel_size, selection_handler = None):
        self._liststore = Gtk.ListStore(GObject.TYPE_PYOBJECT)
        self.set_piecedefs([])
        Gtk.TreeView.__init__(self, self._liststore)
        self.image_pixel_size = image_pixel_size
        self._images_column = Gtk.TreeViewColumn()
        self._images_column.set_title('images')
        self._white_renderer = Gtk.CellRendererPixbuf()
        self._white_renderer.piece_color = 'w'
        self._images_column.pack_start(self._white_renderer, False)
        self._black_renderer = Gtk.CellRendererPixbuf()
        self._black_renderer.piece_color = 's'
        self._images_column.pack_start(self._black_renderer, False)
        self._neutral_renderer = Gtk.CellRendererPixbuf()
        self._neutral_renderer.piece_color = 'n'
        self._images_column.pack_start(self._neutral_renderer, False)
        self._images_column.set_cell_data_func(self._white_renderer, self._image_cell_data, func_data='w')
        self._images_column.set_cell_data_func(self._black_renderer, self._image_cell_data, func_data='s')
        self._images_column.set_cell_data_func(self._neutral_renderer, self._image_cell_data, func_data='n')
        self.append_column(self._images_column)
        self._name_renderer = Gtk.CellRendererText()
        self._name_column = Gtk.TreeViewColumn('name', self._name_renderer)
        self._name_column.set_cell_data_func(self._name_renderer, self._name_cell_data)
        self.append_column(self._name_column)
        if selection_handler != None:
            self.get_selection().connect('changed', selection_handler)

    def set_piecedefs(self, piecedefs):
        self._liststore.clear()
        for piecedef in piecedefs:
            self._liststore.append([piecedef])

    def _image_cell_data(self, _column, _cell, _model, _iter, _data):
        '''
        Callback to provide fill the chess images into the _images_column.
        '''
        piecedef = _model.get_value(_iter, 0)
        _piece_color = _cell.piece_color
        _piece_type = piecedef.piece_symbol[0]
        _piece_rotation = piecedef.piece_symbol[1]
        _image_offset = image_offset(piece_type(_piece_type), piece_color(_piece_color), piece_rotation(_piece_rotation))
        _pixbuf = create_chessimage_pixbuf(_image_offset, self.image_pixel_size)
        LOGGER.debug('_image_cell_data(...) - _piece_color: %s, _piece_type: %s, _piece_rotation: %s, colors: %s'
            % (_piece_color, _piece_type, _piece_rotation, piecedef.colors))
        if piecedef.colors.find(_piece_color) == -1:
            _pixbuf.fill(0xffffffff)
        _cell.set_property('pixbuf', _pixbuf)

    def _name_cell_data(self, _column, _cell, _model, _iter, _data):
        '''
        Callback to fill the name of the fairy piece into the 'name' column.
        '''
        piecedef = _model.get_value(_iter, 0)
        _cell.set_property('text', piecedef.name)

class EditPiecedefsDialog(Gtk.Dialog):
    def __init__(self, problem, memory_db_service, image_pixel_size):
        Gtk.Dialog.__init__(self)
        self.set_title('edit piecedefs')
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.memory_db_service = memory_db_service
        self._problem = problem
        self._selected_piecetype = None
        self._selected_piecedef = None
        self._layout = Gtk.Grid()
        self._layout.show()
        self._layout.set_column_spacing(8)
        self._layout.set_row_homogeneous(True)
        self.get_content_area().pack_start(self._layout, True, True, 0)
        self._piecedefs_listbox = PiecedefsListBox(image_pixel_size, self._on_piecedef_selected)
        self._piecedefs_listbox.set_piecedefs(self._problem.piecedefs)
        self._piecedefs_listbox.set_size_request(200, 200)
        self._piecedefs_listbox.show()
        self._layout.attach(self._piecedefs_listbox, 0, 0, 2, 4)
        self._button_set = Gtk.Button("set")
        self._button_set.set_sensitive(False)
        self._button_set.connect('clicked', self._on_button_set)
        self._button_set.show()
        self._layout.attach(self._button_set, 2, 1, 1, 1)
        self._button_remove = Gtk.Button("remove")
        self._button_remove.set_sensitive(False)
        self._button_remove.show()
        self._layout.attach(self._button_remove, 2, 3, 1, 1)
        self._edit_frame = Gtk.Frame()
        self._edit_frame.show()
        self._layout.attach(self._edit_frame, 3, 0, 2, 4)
        self._search_panel = SearchPanel(PieceTypeSearchProvider(self.memory_db_service), self._on_piecetype_selected)
        self._search_panel.show()
        self._edit_frame.add(self._search_panel)
        self._button_scan_problem = Gtk.Button('scan problem')
        self._button_scan_problem.connect('clicked', self._scan_problem)
        self._button_scan_problem.show()
        self._layout.attach(self._button_scan_problem, 0, 4, 1, 1)

    def _scan_problem(self, widget, data=None):
        _fairy_pieces = {}
        for row in range(self._problem.board.rows):
            for column in range(self._problem.board.columns):
                field = self._problem.board.fields[row][column]
                if not field.is_nofield():
                    piece = field.get_piece()
                    if piece != None and piece.piece_rotation != PIECE_ROTATION_NORMAL:
                        piece_symbol = PIECE_CHARACTERS[piece.piece_type] + PIECE_ROTATIONS[piece.piece_rotation - 1]
                        LOGGER.debug('_scan_problem: found piece_type %d piece_rotation %d: piece_symbol %s' % (piece.piece_type, piece.piece_rotation, piece_symbol))
                        colors = _fairy_pieces.get(piece_symbol, None)
                        color = PIECE_COLORS[piece.piece_color]
                        if colors == None:
                            colors = set([color])
                            _fairy_pieces[piece_symbol] = colors
                        else:
                            colors.add(color)
        _piecedefs = []
        for key in list(_fairy_pieces.keys()):
            color_str = ''
            colors = _fairy_pieces[key]
            if 'w' in colors:
                color_str = color_str + 'w'
            if 's' in colors:
                color_str = color_str + 's'
            if 'n' in colors:
                color_str = color_str + 'n'
            piecedef = PieceDef(color_str, key, '')
            _piecedefs.append(piecedef)
        self._piecedefs_listbox.set_piecedefs(_piecedefs)

    def _on_piecetype_selected(self, piecetype):
        self._selected_piecetype = piecetype
        self._on_selection_changed()

    def _on_piecedef_selected(self, selection):
        model, it = selection.get_selected()
        if it != None:
            self._selected_piecedef = model.get_value(it, 0)
        else:
            self._selected_piecedef = None
        self._on_selection_changed()

    def _on_button_set(self, widget, data=None):
        self._selected_piecedef.name = self._selected_piecetype.get_name()
        self._piecedefs_listbox.queue_draw()

    def _on_selection_changed(self):
        self._button_set.set_sensitive(self._selected_piecetype != None and self._selected_piecedef != None)

    def get_piecedefs(self):
        result = []
        _model = self._piecedefs_listbox.get_model()
        it = _model.get_iter_first()
        while it != None:
            result.append(_model.get_value(it, 0))
            it = _model.iter_next(it)
        return result

class PieceTypeSearchProvider(object):
    def __init__(self, db_service):
        self._db_service = db_service

    def create_liststore(self):
        return Gtk.ListStore(GObject.TYPE_STRING)

    def column_headings(self):
        return ['piece type']

    def filtered_objects(self, name):
        return self._db_service.filter_piecetypes_by_name(name)

    def create_liststore_data(self, piecetype):
        return [piecetype.get_name()]

    def _all_conditions_count(self):
        '''
        Returns the count of conditions inside the database.
        '''
        return self._db_service.count_sources()

    def status_message(self, current_count):
        '''
        Creates a status message for the given number of sources.
        '''
        return '%d of %d conditions' % (current_count, self._all_sources_count())

class EditMultilineTextDialog(Gtk.Dialog):
    def __init__(self, fieldname, text):
        Gtk.Dialog.__init__(self)
        self.set_title('edit ' + fieldname)
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.set_size_request(400, 400)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        self.scrolled_window.show()
        self.text_view = Gtk.TextView()
        self.text_buffer = Gtk.TextBuffer()
        if text == None:
            LOGGER.debug("EditMultilineTextDialog.set_text('')")
            self.text_buffer.set_text('')
        else:
            LOGGER.debug("EditMultilineTextDialog.set_text('%s')" % text)
            self.text_buffer.set_text(text)
        self.text_view.set_buffer(self.text_buffer)
        self.text_view.show()
        self.scrolled_window.add(self.text_view)
        self.get_content_area().pack_start(self.scrolled_window, True, True, 0)

    def get_text(self):
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        text = self.text_buffer.get_slice(start_iter, end_iter, True)
        if len(text) == 0:
            LOGGER.debug('EditMultilineTextDialog.get_text(): no text entered')
            return None
        else:
            LOGGER.debug('EditMultilineTextDialog.get_text(): ' + text)
            return text
