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
This module contains the ui implementation classes of the ChessProblemEditor.
'''
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, Pango

import sys

from .ui_model import ChessProblemModel
from .ui_common import to_model, to_entry
from .board import Board, ColumnLegend, RowLegend, get_legend_strategy, BoardSizeDialog, PieceCountPanel
from .display import AuthorsDisplay, InfoArea, CheckBoxArea
from .input import FastBoardEntry, BoardInputState, BoardInputHandler, ChessImageSelector, ClearFieldSelector, FieldframeSelector, NoFieldSelector
from .help import AboutDialog
from chessproblem.io import ChessProblemLatexParser, write_latex

from chessproblem.image_files import PIECE_TYPE_OFFSETS, PIECE_COLOR_OFFSETS, PIECE_ROTATION_OFFSETS

import chessproblem.model as model
import chessproblem.model.db as db
from chessproblem.model.memory_db import create_memory_db

import logging

from threading import Thread

LOGGER = logging.getLogger('chessproblem.ui')

WINDOW_WIDTH=800
WINDOW_HEIGHT=600

from chessproblem.tools.latex import DialinesTemplate

from chessproblem.tools.popeye import Popeye, call_popeye

from chessproblem.tools.ffen import generate_ffen, parse_ffen

from chessproblem.tools.images import create_image

import copy

class MainFrame(object):
    '''
    The main frame of the ChessProblemEditor application.
    '''
    def __init__(self, cpe_config, filename=None):
        '''
        Initializes the instance.
        If a filename is given, the problems are automatically read from the given file.
        '''
        self.cpe_config = cpe_config
        self.db_service = db.DbService(self.cpe_config.database_url)
        self.memory_db_service = create_memory_db(self.cpe_config.config_dir)
        #
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title(self._make_title())
        self.window.connect("delete_event", self.on_delete)
        self.window.connect("destroy", self.on_destroy)
        self.window_area = Gtk.VBox(False, 0)
        self.window_area.show()
        self.window.add(self.window_area)
        self._create_menu()
        self.model = ChessProblemModel()
        self.model.add_observer(self._on_current_problem_change)
        self.base_area = Gtk.HBox(False, 0)
        self.base_area.set_spacing(8)
        self.base_area.show()
        self.window_area.pack_start(self.base_area, True, True, 0)
        self._create_display_area()
        self.base_area.pack_start(self.display_area, True, True, 0)
        self._create_edit_area()
        self.base_area.pack_start(self.edit_area, True, True, 0)
        self.window.show()
        from os.path import isfile
        self._current_problem_backup = True
        if filename == None or not isfile(filename):
            self.set_filename(filename)
            self._on_current_problem_change()
        else:
            self._open_file(filename)

    def _make_title(self, filename='(New)'):
        return 'ChessProblemEditor - %s' % filename

    def set_filename(self, _new_filename):
        '''
        Registers the _new_filename and changes the ui depending on the
        filename.
        '''
        self._filename = _new_filename;
        if self._filename == None:
            self.file_save_item.set_sensitive(False)
            self.window.set_title(self._make_title())
        else:
            self.file_save_item.set_sensitive(True)
            self.window.set_title(self._make_title('"' + self._filename + '"'))

    def show_error(self, message, details):
        '''
        Used to display an error message and its details.
        '''
        dialog = Gtk.MessageDialog(parent=self.window,
                title='ERROR',
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                message_format=message)
        dialog.set_size_request(500, 500)
        scrolledwindow_details = Gtk.ScrolledWindow()
        scrolledwindow_details.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow_details.show()
        textbuffer_details = Gtk.TextBuffer()
        textbuffer_details.set_text(details)
        textview_details = Gtk.TextView(textbuffer_details)
        textview_details.show()
        scrolledwindow_details.add(textview_details)
        dialog.get_content_area().pack_start(scrolledwindow_details, True, True, 0)
        dialog.run()
        dialog.destroy()


    def _create_display_area(self):
        '''
        This method creates the area (a VBox), which is used to display all problem information.
        '''
        self.display_area = Gtk.VBox(False, 0)
        self.display_area.show()
        self.board_area = Gtk.Grid()
        self.board_area.show()
        self.display_area.pack_start(self.board_area, False, False, 5)
        self.board_display = Board(self.model.current_problem(), self.cpe_config.image_pixel_size)
        self.board_display.show()
        self.board_display.set_click_listener(self._on_board_clicked)
        self.board_window = Gtk.Viewport()
        # self.board_window.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        _SCROLLED_WINDOW_EXTEND = 4
        self.board_window.add(self.board_display)
        self.board_window.set_size_request(
            self.board_display.get_width() + _SCROLLED_WINDOW_EXTEND,
            self.board_display.get_height() + _SCROLLED_WINDOW_EXTEND)
        self.board_window.show()
        self.board_area.attach(self.board_window, 0, 0, 1, 1)
        # Scrollbars
        self.row_scrollbar = Gtk.VScrollbar(self.board_window.get_vadjustment())
        self.row_scrollbar.set_size_request(-1, self.board_display.get_height() + _SCROLLED_WINDOW_EXTEND)
        # self.row_scrollbar.show()
        self.board_area.attach(self.row_scrollbar, 2, 0, 1, 1)
        self.column_scrollbar = Gtk.HScrollbar(self.board_window.get_hadjustment())
        self.column_scrollbar.set_size_request(self.board_display.get_width() + _SCROLLED_WINDOW_EXTEND, -1)
        # self.column_scrollbar.show()
        self.board_area.attach(self.column_scrollbar, 0, 2, 1, 1)
        # Viewports to display our legend
        self.legend_strategy = get_legend_strategy(self.cpe_config.legend_display)
        self.row_legend_viewport = Gtk.Viewport(vadjustment=self.board_window.get_vadjustment())
        self.row_legend = RowLegend(8, self.cpe_config.image_pixel_size)
        self.row_legend.show()
        self.row_legend_viewport.add(self.row_legend)
        self.row_legend_viewport.set_size_request(self.row_legend.get_width(), self.row_legend.get_height())
        self.row_legend_viewport.show()
        self.board_area.attach(self.row_legend_viewport, 1, 0, 1, 1)
        self.column_legend_viewport = Gtk.Viewport(hadjustment=self.board_window.get_hadjustment())
        self.column_legend = ColumnLegend(8, self.cpe_config.image_pixel_size)
        self.column_legend.show()
        self.column_legend_viewport.add(self.column_legend)
        self.column_legend_viewport.set_size_request(self.column_legend.get_width(), self.column_legend.get_height())
        self.column_legend_viewport.show()
        self.board_area.attach(self.column_legend_viewport, 0, 1, 1, 1)
        # Our position input elements
        self.board_input_hbox = Gtk.HBox()
        self.board_input_hbox.show()
        self.display_area.pack_start(self.board_input_hbox, False, False, 5)
        self.board_input_label = Gtk.Label(label='position')
        self.board_input_label.show()
        self.board_input_hbox.pack_start(self.board_input_label, False, False, 8)
        self.board_input_handler = BoardInputHandler(self.model.current_problem(), self.board_display)
        self.board_input_state = BoardInputState(self.board_input_handler)
        self.board_fast_input = FastBoardEntry(self.board_input_state)
        self.board_input_hbox.pack_start(self.board_fast_input, False, False, 8)

        self.label_co = Gtk.Label(label='Co')
        self.label_co.show()
        self.board_input_hbox.pack_start(self.label_co, False, False, 10)
        self.entry_co = Gtk.Entry()
        self.entry_co.show()
        self.board_input_hbox.pack_start(self.entry_co, False, False, 10)

        self.board_piece_count_panel = PieceCountPanel()
        self.board_piece_count_panel.show()
        self.display_area.pack_start(self.board_piece_count_panel, False, False, 5)
        self.board_piece_count_panel.add_current_listener(self._on_piece_count_changed)
        self.board_input_handler.add_piece_listener(self.board_piece_count_panel.piece_listener)
        self.board_input_state.add_piece_color_listener(self._on_piece_color_changed)
        self.board_input_state.add_piece_type_listener(self._on_piece_type_changed)
        self.board_input_state.add_piece_rotation_listener(self._on_piece_rotation_changed)
        input_hbox_1 = Gtk.HBox()
        input_hbox_1.show()
        self.display_area.pack_start(input_hbox_1, False, False, 5)
        self.piece_color_selector = ChessImageSelector(
                self.cpe_config.image_pixel_size,
                image_indexes=[(PIECE_TYPE_OFFSETS[model.PIECE_TYPE_KING] + PIECE_COLOR_OFFSETS[color]) for color in range(model.PIECE_COLOR_COUNT)], horizontal=True)
        self.piece_color_selector.set_selection_listener(self._on_piece_color_selected)
        input_hbox_1.pack_start(self.piece_color_selector, False, False, 0)

        self.piece_rotation_selector = ChessImageSelector(
                self.cpe_config.image_pixel_size,
                image_indexes=[(PIECE_TYPE_OFFSETS[model.PIECE_TYPE_KING] + PIECE_ROTATION_OFFSETS[piece_rotation]) for piece_rotation in range(model.PIECE_ROTATION_COUNT)], horizontal=True)
        self.piece_rotation_selector.set_selection_listener(self._on_piece_rotation_selected)
        input_hbox_1.pack_end(self.piece_rotation_selector, False, False, 0)

        input_hbox_2 = Gtk.HBox()
        input_hbox_2.show()
        self.display_area.pack_start(input_hbox_2, False, False, 5)
        self.piece_type_selector = ChessImageSelector(
                self.cpe_config.image_pixel_size,
                image_indexes=[PIECE_TYPE_OFFSETS[piece_type] for piece_type in range(model.PIECE_TYPE_COUNT)],
                horizontal=True, selected=5)
        self.piece_type_selector.set_selection_listener(self._on_piece_type_selected)
        input_hbox_2.pack_start(self.piece_type_selector, False, False, 0)
        # Another horizontal box for input of empty, framed and missing fields
        input_hbox_3 = Gtk.HBox()
        input_hbox_3.show()
        self.display_area.pack_start(input_hbox_3, False, False, 5)
        self.clear_field_selector = ClearFieldSelector(self.cpe_config.image_pixel_size)
        self.clear_field_selector.set_listener(self._on_clear_field)
        self.clear_field_selector.show()
        input_hbox_3.pack_start(self.clear_field_selector, False, False, 0)
        self.label_clear_field = Gtk.Label(label='clear (-)')
        self.label_clear_field.show()
        input_hbox_3.pack_start(self.label_clear_field, False, False, 5)
        self.fieldframe_selector = FieldframeSelector(self.cpe_config.image_pixel_size)
        self.fieldframe_selector.set_listener(self._on_fieldframe)
        self.fieldframe_selector.show()
        input_hbox_3.pack_start(self.fieldframe_selector, False, False, 5)
        self.label_fieldframe = Gtk.Label(label='fieldframe')
        self.label_fieldframe.show()
        input_hbox_3.pack_start(self.label_fieldframe, False, False, 5)
        self.nofield_selector = NoFieldSelector(self.cpe_config.image_pixel_size)
        self.nofield_selector.set_listener(self._on_nofield)
        self.nofield_selector.show()
        input_hbox_3.pack_start(self.nofield_selector, False, False, 5)
        self.label_nofield = Gtk.Label(label='nofield')
        self.label_nofield.show()
        input_hbox_3.pack_start(self.label_nofield, False, False, 5)
        self.checkbox_area = CheckBoxArea()
        self.checkbox_area.set_visual_change_listener(self._edit_area_visual_change_listener)
        self.display_area.pack_start(self.checkbox_area, False, False, 5)


    def _on_clear_field(self):
        self.board_input_state.set_piece_type(None)

    def _on_fieldframe(self):
        self.board_input_state.mode_fieldframe()

    def _on_nofield(self):
        self.board_input_state.mode_nofields()

    def _create_display_entry(self, width, tooltiptext=None):
        result = Gtk.Entry()
        result.set_size_request(width, -1)
        result.set_editable(False)
        if tooltiptext != None:
            result.set_tooltip_text(tooltiptext)
        result.show()
        return result

    def _create_edit_area(self):
        '''
        This method creates the area (a VBox), which contains the widget to edit the problem information.
        '''
        self.edit_area = Gtk.VBox(False, 2)
        # self.edit_area.set_size_request(WINDOW_WIDTH - 10 * DEFAULT_CONFIG.image_pixel_size, -1)
        self.edit_area.show()
        self.info_area = InfoArea(self.cpe_config, self.db_service, self.memory_db_service, self._edit_area_visual_change_listener)
        self.info_area.show()
        self.edit_area.pack_start(self.info_area, False, False, 0)

    def _edit_area_visual_change_listener(self):
        '''
        Used to handle events e.g. from checkboxes, which should result in a changed board display.
        '''
        LOGGER.debug('MainFrame._edit_area_visual_change_listener()')
        self.board_display.redraw()

    def _on_board_clicked(self, row, column):
        self.board_input_state.field_action(row, column)
        self.board_fast_input.reset()

    def _on_piece_color_selected(self, piece_color):
        self.board_input_state.set_piece_color(piece_color)

    def _on_piece_type_selected(self, piece_type):
        self.board_input_state.set_piece_type(piece_type)

    def _on_piece_rotation_selected(self, piece_rotation):
        self.board_input_state.set_piece_rotation(piece_rotation)

    def _on_piece_color_changed(self, piece_color):
        self.piece_color_selector.set_selected_index(piece_color)

    def _on_piece_type_changed(self, piece_type):
        self.piece_type_selector.set_selected_index(piece_type)

    def _on_piece_rotation_changed(self, piece_rotation):
        self.piece_rotation_selector.set_selected_index(piece_rotation)

    def _on_piece_count_changed(self, white, black, neutral):
        '''
        Called when the number of pieces on the board has changed.
        We need to change the status bar containing a display for this value.
        '''
        if neutral == 0:
            piece_count_value = '(' + str(white) + '+' + str(black) + ')'
        else:
            piece_count_value = '(' + str(white) + '+' + str(black) + '+' + str(neutral) + 'n)'
        self.piece_count_status_bar.remove_all(self.piece_count_context_id)
        self.piece_count_status_bar.push(self.piece_count_context_id, piece_count_value)


    def _create_menu(self):
        '''
        Creates our applications main menu.
        '''
        self.menu_bar = Gtk.MenuBar()
        accel_group = Gtk.AccelGroup()
        self.window.add_accel_group(accel_group)

        # Our file menu
        self.file_menu_item = Gtk.MenuItem("File")
        self.file_menu_item.show()
        self.file_menu = Gtk.Menu()
        self.file_menu_item.set_submenu(self.file_menu)
        # file menu items
        self.file_new_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'New', self.on_file_new, accel_group, ord('N'), Gdk.ModifierType.CONTROL_MASK)
        self.file_open_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Open', self.on_file_open, accel_group, ord('O'), Gdk.ModifierType.CONTROL_MASK)
        self.file_save_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Save', self.on_file_save, accel_group, ord('S'), Gdk.ModifierType.CONTROL_MASK)
        self.file_save_item.set_sensitive(False)
        self.file_save_as_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Save As', self.on_file_save_as, accel_group, ord('A'), Gdk.ModifierType.CONTROL_MASK)
        sep = Gtk.SeparatorMenuItem()
        sep.show()
        self.file_menu.append(sep)
        self.file_exit_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Exit', self.on_file_exit, accel_group, ord('Q'), Gdk.ModifierType.CONTROL_MASK)
        self.menu_bar.append(self.file_menu_item)

        # Our problems menu
        self.problems_menu_item = Gtk.MenuItem("Problems")
        self.problems_menu_item.show()
        self.problems_menu = Gtk.Menu()
        self.problems_menu_item.set_submenu(self.problems_menu)
        # problems menu items
        self.problems_first_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'First', self.on_problems_first, accel_group, 65360)
        self.problems_previous_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Previous', self.on_problems_previous, accel_group, 65365)
        self.problems_previous_item.set_sensitive(False)
        self.problems_next_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Next', self.on_problems_next, accel_group, 65366)
        self.problems_next_item.set_sensitive(False)
        self.problems_last = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Last', self.on_problems_last, accel_group, 65367)
        sep = Gtk.SeparatorMenuItem()
        sep.show()
        self.problems_menu.append(sep)
        self.problems_insert_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Insert', self.on_problems_insert, accel_group, 65379, Gdk.ModifierType.SHIFT_MASK)
        self.problems_append_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Append', self.on_problems_append, accel_group, 65293, Gdk.ModifierType.SHIFT_MASK)
        self.problems_delete_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Delete', self.on_problems_delete, accel_group, 65535, Gdk.ModifierType.SHIFT_MASK)
        self.menu_bar.append(self.problems_menu_item)
        sep = Gtk.SeparatorMenuItem()
        sep.show()
        self.problems_menu.append(sep)
        self.problems_change_boardsize_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Change board size', self.on_change_boardsize, accel_group, ord('B'), Gdk.ModifierType.CONTROL_MASK)

        self.menu_bar.show()
        # The LaTeX menu
        if len(self.cpe_config.compile_menu_actions) > 0:
            self.compile_menu_item = Gtk.MenuItem('LaTeX')
            self.compile_menu_item.show()
            self.compile_menu = Gtk.Menu()
            self.compile_menu_item.set_submenu(self.compile_menu)
            for values in self.cpe_config.compile_menu_actions:
                (menu_label, workdir, template_file, include_file, target_file) = values
                menu_item = Gtk.MenuItem(menu_label)
                menu_item.show()
                menu_item.connect('activate', self._on_compile_menu,
                    DialinesTemplate(self.cpe_config, workdir, template_file, include_file, target_file, self.show_error).execute)
                self.compile_menu.append(menu_item)
            self.menu_bar.append(self.compile_menu_item)
        # The popeye menu
        if self.cpe_config.popeye_executable != None:
            self.popeye_menu_item = Gtk.MenuItem('Popeye')
            self.popeye_menu_item.show()
            self.popeye_menu = Gtk.Menu()
            self.popeye_menu_item.set_submenu(self.popeye_menu)
            self.popeye_menu_item_current_problem = Gtk.MenuItem('current problem input')
            self.popeye_menu_item_current_problem.show()
            self.popeye_menu_item_current_problem.connect('activate', self._on_popeye_current_problem)
            self.popeye_menu.append(self.popeye_menu_item_current_problem)
            self.popeye_menu_item_all_problems = Gtk.MenuItem('all problems input')
            self.popeye_menu_item_all_problems.show()
            self.popeye_menu_item_all_problems.connect('activate', self._on_popeye_all_problems)
            self.popeye_menu.append(self.popeye_menu_item_all_problems)
            self.menu_bar.append(self.popeye_menu_item)
        # The tools menu
        self.tools_menu_item = Gtk.MenuItem('Tools')
        self.tools_menu_item.show()
        self.tools_menu = Gtk.Menu()
        self.tools_menu_item.set_submenu(self.tools_menu)
        self.tools_menu_item_ffen = Gtk.MenuItem('Generate Fairy FEN')
        self.tools_menu_item_ffen.show()
        self.tools_menu_item_ffen.connect('activate', self._on_ffen_current_problem)
        self.tools_menu.append(self.tools_menu_item_ffen)
        self.tools_menu_item_import_ffen = Gtk.MenuItem('Import from Fairy FEN')
        self.tools_menu_item_import_ffen.show()
        self.tools_menu_item_import_ffen.connect('activate', self._on_import_ffen)
        self.tools_menu.append(self.tools_menu_item_import_ffen)
        self.tools_menu_item_png = Gtk.MenuItem('Save board as PNG image')
        self.tools_menu_item_png.show()
        self.tools_menu_item_png.connect('activate', self._on_png_image)
        self.tools_menu.append(self.tools_menu_item_png)
        self.menu_bar.append(self.tools_menu_item)
        # The help menu
        self.help_menu_item = Gtk.MenuItem('Help')
        self.help_menu_item.show()
        self.help_menu = Gtk.Menu()
        self.help_menu_item.set_submenu(self.help_menu)
        self.help_about_item = Gtk.MenuItem('About')
        self.help_about_item.show()
        self.help_about_item.connect('activate', self._on_help_about)
        self.help_menu.append(self.help_about_item)
        self.menu_bar.append(self.help_menu_item)
        # Add the menu bar to the window
        self.window_area.pack_start(self.menu_bar, False, False, 0)

        # Add a status bar
        self.status_box = Gtk.HBox()
        self.status_box.show()
        self.window_area.pack_end(self.status_box, False, False, 0)
        self.problem_index_status_bar = Gtk.Statusbar()
        # self.problem_index_status_bar.set_has_resize_grip(False)
        self.problem_index_status_bar.set_size_request(120, -1)
        self.problem_index_status_bar.show()
        self.status_box.pack_start(self.problem_index_status_bar, False, False, 0)
        self.problem_position_context_id = self.problem_index_status_bar.get_context_id('problem_position')
        self.problem_position_message_id = self.problem_index_status_bar.push(self.problem_position_context_id, 'Problem 1 of 1')
        self.piece_count_status_bar = Gtk.Statusbar()
        self.piece_count_status_bar.show()
        self.status_box.pack_start(self.piece_count_status_bar, True, True, 0)
        self.piece_count_context_id = self.piece_count_status_bar.get_context_id('piece_count')
        self.piece_count_message_id = self.piece_count_status_bar.push(self.piece_count_context_id, '(0+0)')


    def _add_menu_item_with_accelerator(self, menu, label, handler, accel_group, accel_char, key_modifier=0):
        result = self._add_menu_item(menu, label, handler)
        result.add_accelerator('activate', accel_group, accel_char, key_modifier, Gtk.AccelFlags.VISIBLE)
        return result

    def _add_menu_item(self, menu, label, handler):
        result = Gtk.MenuItem(label)
        result.show()
        result.connect('activate', handler, None)
        menu.append(result)
        return result

    def _new_backup_copy(self):
        LOGGER.debug('Creating new backup copy')
        self._current_problem_backup = copy.deepcopy(self.model.current_problem())

    def ignore_unsaved_changes(self):
        '''
        When there are unsafed changes, the method pops up a dialog 
        asking for confirmation to continue without saving.
        Returns:
        -   true:   there are no unsafed changes or the user wants not to safe the changes
        -   false:  the user stop the current action
        '''
        self._store_changes_to_problem()
        if self.has_changes():
            dialog = Gtk.MessageDialog(parent=self.window,
                    title='WARNING',
                    flags=Gtk.DialogFlags.MODAL,
                    message_type=Gtk.MessageType.WARNING,
                    buttons=Gtk.ButtonsType.YES_NO,
                    message_format='There are unsaved changes. Do you want to continue without saving?')
            response = dialog.run()
            result = (response == Gtk.ResponseType.YES)
            dialog.destroy()
            return result
        else:
            return True

    def has_changes(self):
        '''
        As long as we had no changes, we keep a backup copy of the current
        problem in _current_problem_backup.
        When we have found a change, we set _current_problem_backup to None to
        -   mark the document as changed
        -   avoid any further comparisons.
        '''
        result = self._current_problem_backup == None
        LOGGER.debug('has_changes() -> %r' % result)
        return result

    def _check_changes(self):
        if self._current_problem_backup != None:
            if not model.chessproblems_equal(self._current_problem_backup, self.model.current_problem()):
                LOGGER.debug('_check_changes() - new changes detected')
                self._current_problem_backup = None

    def _store_changes_to_problem(self):
        '''
        This method needs to be called to transfer input data to the current problem.
        '''
        self.info_area.save_to_problem()
        self.checkbox_area.save_to_problem()
        self.model.current_problem().Co = to_model(self.entry_co.get_text())
        (white, black, neutral) = self.board_piece_count_panel.get_control_counters()
        if (white, black, neutral) != (0, 0, 0):
            piece_counter = model.PieceCounter(white, black, neutral)
        else:
            piece_counter = None
        self.model.current_problem().pieces_control = piece_counter
        self._check_changes()

    def on_problems_first(self, widget, event, data=None):
        '''
        Called when user wants to switch to the first problem.
        '''
        self._store_changes_to_problem()
        self.model.first_problem()

    def on_problems_previous(self, widget, event, data=None):
        '''
        Called when user wants to switch to the previous problem.
        '''
        self._store_changes_to_problem()
        self.model.previous_problem()

    def on_problems_next(self, widget, event, data=None):
        '''
        Called when user wants to switch to the next problem.
        '''
        self._store_changes_to_problem()
        self.model.next_problem()

    def on_problems_last(self, widget, event, data=None):
        '''
        Called when user wants to switch to the last problem.
        '''
        self._store_changes_to_problem()
        self.model.last_problem()

    def on_problems_insert(self, widget, event, data=None):
        '''
        Called when the user wants to insert a new problem before the current one.
        '''
        self._store_changes_to_problem()
        self._current_problem_backup = None
        self.model.insert_problem()

    def on_problems_append(self, widget, event, data=None):
        '''
        Called when the user wants to insert a new problem after the current one.
        '''
        self._store_changes_to_problem()
        self._current_problem_backup = None
        self.model.append_problem()

    def on_problems_delete(self, widget, event, data=None):
        '''
        Called when the user wants to delete the current problem.
        '''
        dialog = Gtk.MessageDialog(parent=self.window,
                title='delete current problem',
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                message_format='Are you sure to delete the problem?')
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            self._current_problem_backup = None
            self.model.delete_problem()
        dialog.destroy()

    def on_change_boardsize(self, widget, event, data=None):
        '''
        Called when the user selects the menu entry "change board size".
        '''
        board = self.model.current_problem().board
        dialog = BoardSizeDialog(board.rows, board.columns)
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            board.resize(dialog.get_rows(), dialog.get_columns())
            self._on_current_problem_change()
        dialog.destroy()

    def _on_compile_menu(self, widget, data=None):
        '''
        Called when one of the (document) tools menu items is selected.
        The 'data' parameter contains the document method to be called.
        '''
        self._store_changes_to_problem()
        Thread(target=data(self.model.get_document())).run()

    def _on_popeye_current_problem(self, widget, data=None):
        '''
        Called when the 'Current Problem' entry of the popeye menu is selected.
        '''
        self._store_changes_to_problem()
        popeye_input_factory = Popeye(self.memory_db_service)
        popeye_input = popeye_input_factory.create_popeye_input(self.model.current_problem())
        popeye_dialog = PopeyeDialog(popeye_input)
        response = popeye_dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            call_popeye(popeye_dialog.get_text(), self.cpe_config)
        popeye_dialog.destroy()

    def _on_popeye_all_problems(self, widget, data=None):
        '''
        Called when the 'all problems' entry of the popeye menu is selected.
        '''
        self._store_changes_to_problem()
        popeye_input_factory = Popeye(self.memory_db_service)
        popeye_input = popeye_input_factory.create_popeye_input(self.model.get_document())
        popeye_dialog = PopeyeDialog(popeye_input)
        response = popeye_dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            call_popeye(popeye_dialog.get_text(), self.cpe_config)
        popeye_dialog.destroy()

    def _on_ffen_current_problem(self, widget, data=None):
        '''
        Called when the 'Fairy FEN' entry of the 'tools' menu is selected.
        '''
        self._store_changes_to_problem()
        try:
            _ffen = generate_ffen(self.model.current_problem())
        except Exception as e:
            _ffen = str(e)
        ffen_dialog = FFENDialog(self.window, 'Generated Fairy FEN', _ffen)
        ffen_dialog.run()
        ffen_dialog.destroy()

    def _on_import_ffen(self, widget, data=None):
        '''
        Called when the 'Import from Fairy FEN' entry of the 'tools' menu is selected.
        '''
        do_import = True
        if not model.boards_equal(model.Board(), self.model.current_problem().board):
            dialog = Gtk.MessageDialog(parent=self.window,
                    title='Import from FFEN - WARNING',
                    flags=Gtk.DialogFlags.MODAL,
                    message_type=Gtk.MessageType.WARNING,
                    buttons=Gtk.ButtonsType.YES_NO,
                    message_format='The current board is not empty!\nDo you want to overwrite its contents?')
            response = dialog.run()
            do_import = (response == Gtk.ResponseType.YES)
            dialog.destroy()
        if do_import:
            dialog = FFENDialog(self.window, 'Enter Fairy FEN to import ...')
            response = dialog.run()
            if response == Gtk.ResponseType.ACCEPT:
                ffen = dialog.get_ffen()
                board = parse_ffen(ffen)
                self.model.current_problem().board = board
                self._on_current_problem_change()
                self._current_problem_backup = None
            dialog.destroy()

    def _on_png_image(self, widget, data=None):
        '''
        Called when the 'PNG Image' entry of the 'tools' menu is selected.
        '''
        self._store_changes_to_problem()
        dialog = Gtk.FileChooserDialog(
                title='Save PNG Image as ...',
                action=Gtk.FileChooserAction.SAVE,
                buttons=(
                    Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if filename != None:
                image = create_image(self.model.current_problem(), self.cpe_config.png_pixel_size)
                image.save(filename)
        else:
            LOGGER.info('_on_png_image: No files selected')
        dialog.destroy()


    def on_file_new(self, widget, event, data=None):
        '''
        Event handler for menu entry File / New.
        '''
        if self.ignore_unsaved_changes():
            self.set_filename(None)
            self.model.set_document(model.ChessproblemDocument())
            self._new_backup_copy()

    def _open_file(self, filename):
        '''
        Registers the given filename and reads the problems from this file.
        '''
        self.set_filename(filename)
        with open(filename, 'r', encoding='utf-8') as f:
            s = f.read()
            parser = ChessProblemLatexParser(self.cpe_config, self.memory_db_service)
            document = parser.parse_latex_str(s)
            self.model.set_document(document)
        self._new_backup_copy()


    def on_file_open(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Open.
        '''
        dialog = Gtk.FileChooserDialog(
                title='Open file', action=Gtk.FileChooserAction.OPEN,
                buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self._open_file(filename)
        else:
            LOGGER.info('on_file_open: No files selected')
        dialog.destroy()

    def on_file_save(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Save.
        '''
        if self._filename != None:
            self._save_file()
        else:
            LOGGER.warn('on_file_save called without a registered filename.')

    def on_file_save_as(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Save As.
        '''
        dialog = Gtk.FileChooserDialog(
                title='Save as ...',
                action=Gtk.FileChooserAction.SAVE,
                buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if filename != None:
                self.set_filename(filename)
                self._save_file()
        else:
            LOGGER.info('on_file_open: No files selected')
        dialog.destroy()

    def _save_file(self):
        '''
        Saves the current problemlist into the file with the registered filename.
        '''
        self._store_changes_to_problem()
        with open(self._filename, 'w', encoding='utf-8') as f:
            write_latex(self.model.get_document(), f)
        self._new_backup_copy()

    def on_file_exit(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Exit.
        '''
        if self.ignore_unsaved_changes():
            self.quit()


    def on_delete(self, widget, event, data=None):
        '''
        Called when the application should be closed.
        '''
        return not self.ignore_unsaved_changes()

    def on_destroy(self, widget, data=None):
        '''
        Called when the destroy_event occurs.
        '''
        self.quit()

    def _on_current_problem_change(self):
        '''
        This method is registered as observer to changes to the current selected problem within the list of problems.
        It is used change the display and adjust the statusbar accordingly.
        '''
        current_problem = self.model.current_problem()
        if current_problem.board.rows <= 8:
            self.row_scrollbar.hide()
        else:
            self.row_scrollbar.show()
        self.legend_strategy(self.row_scrollbar, self.row_legend_viewport)
        self.row_legend.set_rows(current_problem.board.rows)
        if current_problem.board.columns <= 8:
            self.column_scrollbar.hide()
        else:
            self.column_scrollbar.show()
        self.legend_strategy(self.column_scrollbar, self.column_legend_viewport)
        self.column_legend.set_columns(current_problem.board.columns)
        self.board_input_handler.set_problem(current_problem)
        self.entry_co.set_text(to_entry(current_problem.Co))
        self.info_area.set_problem(current_problem)
        self.checkbox_area.set_problem(current_problem)
        self.board_display.set_chessproblem(current_problem)
        if current_problem.pieces_control != None:
            self.board_piece_count_panel.set_control_counters(
                    current_problem.pieces_control.count_white, 
                    current_problem.pieces_control.count_black, 
                    current_problem.pieces_control.count_neutral)
        else:
            self.board_piece_count_panel.set_control_counters(0, 0, 0)
        (white, black, neutral) = current_problem.board.get_pieces_count()
        self.board_piece_count_panel.set_current_values(white, black, neutral)
        # Adjust Statusbar
        self.problem_index_status_bar.remove_all(self.problem_position_context_id)
        self.problem_position_message_id = self.problem_index_status_bar.push(
                self.problem_position_context_id,
                'problem %d of %d' % (self.model.current_problem_index + 1, self.model.get_problem_count()))
        # Adjust enabled/disabled navigation menus
        self.problems_previous_item.set_sensitive(not self.model.is_first_problem())
        self.problems_next_item.set_sensitive(not self.model.is_last_problem())
        # Clone the new current problem for change detection, if no changes
        # have been detected before
        if self._current_problem_backup != None:
            self._current_problem_backup = copy.deepcopy(current_problem)

    def _on_help_about(self, widget, data=None):
        dialog = AboutDialog(self.cpe_config, self.memory_db_service)
        dialog.run()
        dialog.destroy()

    def quit(self):
        Gtk.main_quit()
        sys.exit(0)

    def main(self):
        Gtk.main()

class PopeyeDialog(Gtk.Dialog):
    '''
    A dialog, which allows to edit the generated popeye input, in case
    ChessProblemEditor does not support everything needed.
    '''
    def __init__(self, popeye_input):
        Gtk.Dialog.__init__(self)
        self.set_title('Popeye / solve current problem')
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.set_size_request(500, 500)
        self.scrolledwindow_popeye_input = Gtk.ScrolledWindow()
        self.scrolledwindow_popeye_input.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow_popeye_input.show()
        self.textview_popeye_input = Gtk.TextView()
        self.textview_popeye_input.show()
        self.text_buffer = self.textview_popeye_input.get_buffer()
        LOGGER.debug('PopeyeDialog.set_text(%s)' % popeye_input)
        self.text_buffer.set_text(popeye_input)
        self.scrolledwindow_popeye_input.add(self.textview_popeye_input)
        self.get_content_area().pack_start(self.scrolledwindow_popeye_input, True, True, 0)
        self.textview_popeye_input = Gtk.TextView()
        self.textview_popeye_input.show()

    def get_text(self):
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        result = self.text_buffer.get_text(start_iter, end_iter, True)
        LOGGER.debug('PopeyeDialog.get_text() => %s' % result)
        return result

class FFENDialog(Gtk.Dialog):
    '''
    A dialog, to edit or display the FFEN for the current problem
    '''
    def __init__(self, parent, title, ffen=None):
        Gtk.Dialog.__init__(self,  parent=parent)
        self.set_title(title)
        self.set_modal(True)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        if ffen == None:
            self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.set_size_request(500, 100)
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.show()
        self.textview = Gtk.TextView()
        self.textview.set_editable(ffen == None)
        self.textview.show()
        self.text_buffer = self.textview.get_buffer()
        if ffen == None:
            self.text_buffer.set_text('')
        else:
            self.text_buffer.set_text(ffen)
        self.scrolledwindow.add(self.textview)
        self.get_content_area().pack_start(self.scrolledwindow, True, True, 0)

    def get_ffen(self):
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        result = self.text_buffer.get_text(start_iter, end_iter, True)
        LOGGER.debug('FFENDialog.get_ffen() => %s' % result)
        return result



