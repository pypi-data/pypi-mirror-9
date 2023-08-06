from PySide import QtCore, QtGui
from PySide.QtGui import QStyle

from maverig.data import dataHandler
from maverig.views import abstractView


class MenuBarView(QtGui.QMenuBar, abstractView.AbstractView):
    """Represents the menu bar."""

    def __init__(self):
        super(MenuBarView, self).__init__()

        self.action_new = None
        self.action_open = None
        self.action_save = None
        self.action_save_as = None
        self.action_settings = None
        self.action_quit = None

        self.action_undo = None
        self.action_redo = None
        self.action_auto_layout = None
        self.action_cut = None
        self.action_copy = None
        self.action_paste = None
        self.action_delete = None
        self.action_select_all = None

        self.action_back_to_start = None
        self.action_reduce_speed = None
        self.action_run = None
        self.action_stop = None
        self.action_pause = None
        self.action_increase_speed = None
        self.action_forward_to_end = None
        self.action_set_time = None
        self.action_go_to_time = None

        self.action_hand_mode = None
        self.action_selection_mode = None
        self.action_raster_mode = None
        self.action_zoom_in = None
        self.action_zoom_out = None
        self.action_zoom_fit = None
        self.action_trigger_component_panel = None
        self.action_trigger_property_panel = None
        self.action_trigger_console = None
        self.action_trigger_status_bar = None
        self.action_trigger_progress_bar = None
        self.action_trigger_attribute_panel = None

        self.action_help = None
        self.action_about = None

    def init_ui(self):
        self.setGeometry(QtCore.QRect(0, 0, 808, 21))

        # adds file menu
        menu_file = QtGui.QMenu(self)
        menu_file.setTitle(_("File"))

        # adds edit menu
        menu_edit = QtGui.QMenu(self)
        menu_edit.setTitle(_("Edit"))

        # adds simulation menu
        menu_simulation = QtGui.QMenu(self)
        menu_simulation.setTitle(_("Simulation"))

        # adds view menu
        menu_view = QtGui.QMenu(self)
        menu_view.setTitle(_("View"))

        # adds help menu
        menu_help = QtGui.QMenu(self)
        menu_help.setTitle(_("Help"))

        # adds file menu actions
        self.action_new = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/new.png')), _('New'), self,
                                        shortcut="Ctrl+N")
        self.action_new.setText(_("New"))
        self.action_new.triggered.connect(self.associated_presenter.on_file_new_triggered)
        menu_file.addAction(self.action_new)

        self.action_open = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/fileopen.png')), _('Open'), self,
                                         shortcut="Ctrl+O")
        self.action_open.setText(_("Open"))
        self.action_open.triggered.connect(self.associated_presenter.on_file_open_triggered)
        menu_file.addAction(self.action_open)

        menu_file.addSeparator()

        self.action_save = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/filesave.png')), _('Save'), self,
                                         shortcut="Ctrl+S")
        self.action_save.setText(_("Save"))
        self.action_save.triggered.connect(self.associated_presenter.on_file_save_triggered)
        menu_file.addAction(self.action_save)

        self.action_save_as = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/filesave.png')), _('Save As...'),
                                            self,
                                            shortcut="Ctrl+Shift+S")
        self.action_save_as.setText(_("Save As..."))
        self.action_save_as.triggered.connect(self.associated_presenter.on_file_save_as_triggered)
        menu_file.addAction(self.action_save_as)

        menu_file.addSeparator()

        self.action_settings = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/settings.png')),
                                             _('Preferences'), self)
        self.action_settings.setText(_("Preferences"))
        self.action_settings.triggered.connect(self.associated_presenter.on_settings_triggered)
        menu_file.addAction(self.action_settings)

        menu_file.addSeparator()

        self.action_quit = QtGui.QAction(self.style().standardIcon(QStyle.SP_DialogCloseButton), _('Quit'), self,
                                         shortcut="Ctrl+Q")
        self.action_quit.setText(_("Quit"))
        self.action_quit.triggered.connect(self.associated_presenter.on_quit_triggered)
        menu_file.addAction(self.action_quit)

        # adds edit menu actions
        self.action_undo = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/undo.png')), _('Undo'), self,
                                         shortcut="Ctrl+Z")
        self.action_undo.setText(_("Undo"))
        self.action_undo.triggered.connect(self.associated_presenter.on_undo_triggered)
        menu_edit.addAction(self.action_undo)

        self.action_redo = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/redo.png')), _('Redo'), self,
                                         shortcut="Ctrl+Y")
        self.action_redo.setText(_("Redo"))
        self.action_redo.triggered.connect(self.associated_presenter.on_redo_triggered)
        menu_edit.addAction(self.action_redo)

        menu_edit.addSeparator()

        self.action_auto_layout = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/auto_layout.png')),
                                                _('Auto Layout'), self, shortcut="F4")
        self.action_auto_layout.setText(_("Auto Layout"))
        self.action_auto_layout.triggered.connect(self.associated_presenter.on_auto_layout_triggered)
        menu_edit.addAction(self.action_auto_layout)

        menu_edit.addSeparator()

        self.action_cut = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/cut.png')), _('Cut'), self,
                                        shortcut="Ctrl+X")
        self.action_cut.setText(_("Cut"))
        self.action_cut.triggered.connect(self.associated_presenter.on_cut_triggered)
        menu_edit.addAction(self.action_cut)

        self.action_copy = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/copy.png')), _('Copy'), self,
                                         shortcut="Ctrl+C")
        self.action_copy.setText(_("Copy"))
        self.action_copy.triggered.connect(self.associated_presenter.on_copy_triggered)
        menu_edit.addAction(self.action_copy)

        self.action_paste = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/paste.png')), _('Paste'),
                                          self, shortcut="Ctrl+V")
        self.action_paste.setText(_("Paste"))
        self.action_paste.triggered.connect(self.associated_presenter.on_paste_triggered)
        menu_edit.addAction(self.action_paste)

        self.action_delete = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/delete.png')), _('Delete'),
                                           self, shortcut="Del")
        self.action_delete.setText(_("Delete"))
        self.action_delete.triggered.connect(self.associated_presenter.on_delete_triggered)
        menu_edit.addAction(self.action_delete)

        self.action_select_all = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/select_all.png')),
                                               _('Select All'), self, shortcut="Ctrl+A")
        self.action_select_all.setText(_("Select All"))
        self.action_select_all.triggered.connect(self.associated_presenter.on_select_all_triggered)
        menu_edit.addAction(self.action_select_all)

        # add simulation menu actions
        self.action_run = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/vid_start.png')), _('Run'), self,
                                        shortcut="F5")
        self.action_run.triggered.connect(self.associated_presenter.on_run_triggered)
        menu_simulation.addAction(self.action_run)

        self.action_stop = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/vid_stop.png')), _('Stop'), self,
                                         shortcut="F6")
        self.action_stop.setDisabled(True)
        self.action_stop.triggered.connect(self.associated_presenter.on_stop_triggered)
        menu_simulation.addAction(self.action_stop)

        self.action_pause = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/vid_pause.png')), _('Pause'),
                                          self, shortcut="F7")
        self.action_pause.triggered.connect(self.associated_presenter.on_pause_triggered)
        self.action_pause.setDisabled(True)
        menu_simulation.addAction(self.action_pause)

        menu_simulation.addSeparator()

        self.action_back_to_start = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/vid_back_to_start.png')),
                                                  _('Back to start'), self, shortcut="F8")
        self.action_back_to_start.triggered.connect(self.associated_presenter.on_back_to_start_triggered)
        self.action_back_to_start.setDisabled(True)
        menu_simulation.addAction(self.action_back_to_start)

        self.action_reduce_speed = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/vid_back.png')),
                                                 _('Reduce speed'), self, shortcut="F9")
        self.action_reduce_speed.triggered.connect(self.associated_presenter.on_reduce_speed_triggered)
        self.action_reduce_speed.setDisabled(True)
        menu_simulation.addAction(self.action_reduce_speed)

        self.action_increase_speed = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/vid_forward.png')),
                                                   _('Increase speed'), self, shortcut="F10")
        self.action_increase_speed.triggered.connect(self.associated_presenter.on_increase_speed_triggered)
        self.action_increase_speed.setDisabled(True)
        menu_simulation.addAction(self.action_increase_speed)

        self.action_forward_to_end = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/vid_forward_to_end.png')),
                                                   _('Forward to end'), self, shortcut="F11")
        self.action_forward_to_end.triggered.connect(self.associated_presenter.on_forward_to_end_triggered)
        self.action_forward_to_end.setDisabled(True)
        menu_simulation.addAction(self.action_forward_to_end)

        menu_simulation.addSeparator()

        self.action_set_time = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/time.png')),
                                             _('Set Time'),
                                             self, shortcut="Ctrl+T")
        self.action_set_time.triggered.connect(self.associated_presenter.on_set_time_triggered)
        menu_simulation.addAction(self.action_set_time)

        self.action_go_to_time = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/time.png')),
                                               _('Go To'),
                                               self, shortcut="Ctrl+G")
        self.action_go_to_time.triggered.connect(self.associated_presenter.on_go_to_triggered)
        self.action_go_to_time.setDisabled(True)
        menu_simulation.addAction(self.action_go_to_time)

        # adds view menu actions
        self.action_hand_mode = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/hand_mode.png')),
                                              _('Shift mode'), self, shortcut="Ctrl+Alt+H")
        self.action_hand_mode.setText(_("Shift mode"))
        self.action_hand_mode.setCheckable(True)
        self.action_hand_mode.triggered.connect(self.associated_presenter.on_hand_mode_triggered)
        menu_view.addAction(self.action_hand_mode)

        self.action_selection_mode = QtGui.QAction(
            QtGui.QIcon(dataHandler.get_icon('menubar/selection_mode.png')),
            _('Selection mode'), self, shortcut="Ctrl+Alt+S")
        self.action_selection_mode.setText(_("Selection mode"))
        self.action_selection_mode.setCheckable(True)
        self.action_selection_mode.triggered.connect(self.associated_presenter.on_selection_mode_triggered)
        menu_view.addAction(self.action_selection_mode)

        menu_view.addSeparator()

        self.action_raster_mode = QtGui.QAction(
            QtGui.QIcon(dataHandler.get_icon('menubar/raster_mode.png')),
            _('Snap dragged elements to raster'), self, shortcut="Ctrl+Alt+R")
        self.action_raster_mode.setText(_("Raster"))
        self.action_raster_mode.triggered.connect(self.associated_presenter.on_raster_mode_triggered)
        self.action_raster_mode.setCheckable(True)
        menu_view.addAction(self.action_raster_mode)

        menu_view.addSeparator()

        self.action_zoom_in = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/zoom_in.png')),
                                            _('Zoom In'),
                                            self, shortcut="Ctrl++")
        self.action_zoom_in.setText(_("Zoom In"))
        self.action_zoom_in.triggered.connect(self.associated_presenter.on_zoom_in_triggered)
        menu_view.addAction(self.action_zoom_in)

        self.action_zoom_out = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/zoom_out.png')),
                                             _('Zoom Out'),
                                             self, shortcut="Ctrl+-")
        self.action_zoom_out.setText(_("Zoom Out"))
        self.action_zoom_out.triggered.connect(self.associated_presenter.on_zoom_out_triggered)
        menu_view.addAction(self.action_zoom_out)

        self.action_zoom_fit = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/zoom_fit.png')), _('Zoom Fit'),
                                             self, shortcut="Ctrl+.")
        self.action_zoom_fit.setText(_("Zoom Fit"))
        self.action_zoom_fit.triggered.connect(self.associated_presenter.on_zoom_fit_triggered)
        menu_view.addAction(self.action_zoom_fit)

        menu_view.addSeparator()

        self.action_trigger_component_panel = QtGui.QAction(_('Show mode panel'), self, shortcut="Ctrl+1")
        self.action_trigger_component_panel.setText(_("Mode panel"))
        self.action_trigger_component_panel.triggered.connect(self.associated_presenter.on_trigger_component_panel)
        self.action_trigger_component_panel.setCheckable(True)
        menu_view.addAction(self.action_trigger_component_panel)

        self.action_trigger_property_panel = QtGui.QAction(_('Show property panel'), self, shortcut="Ctrl+2")
        self.action_trigger_property_panel.setText(_("Property panel"))
        self.action_trigger_property_panel.triggered.connect(self.associated_presenter.on_trigger_property_panel)
        self.action_trigger_property_panel.setCheckable(True)
        menu_view.addAction(self.action_trigger_property_panel)

        self.action_trigger_console = QtGui.QAction(_('Show console panel'), self, shortcut="Ctrl+3")
        self.action_trigger_console.setText(_("Console panel"))
        self.action_trigger_console.triggered.connect(self.associated_presenter.on_trigger_console)
        self.action_trigger_console.setCheckable(True)
        menu_view.addAction(self.action_trigger_console)

        self.action_trigger_status_bar = QtGui.QAction(_('Show status bar'), self, shortcut="Ctrl+4")
        self.action_trigger_status_bar.setText(_("Status bar"))
        self.action_trigger_status_bar.triggered.connect(self.associated_presenter.on_trigger_status_bar)
        self.action_trigger_status_bar.setCheckable(True)
        menu_view.addAction(self.action_trigger_status_bar)

        self.action_trigger_progress_bar = QtGui.QAction(_('Show progress panel'), self, shortcut="Ctrl+5")
        self.action_trigger_progress_bar.setText(_("Progress panel"))
        self.action_trigger_progress_bar.triggered.connect(self.associated_presenter.on_trigger_progress_bar)
        self.action_trigger_progress_bar.setDisabled(True)
        self.action_trigger_progress_bar.setCheckable(True)
        menu_view.addAction(self.action_trigger_progress_bar)

        self.action_trigger_attribute_panel = QtGui.QAction(_('Show attributes panel'), self, shortcut="Ctrl+6")
        self.action_trigger_attribute_panel.setText(_("Attributes panel"))
        self.action_trigger_attribute_panel.triggered.connect(self.associated_presenter.on_trigger_attribute_panel)
        self.action_trigger_attribute_panel.setDisabled(True)
        self.action_trigger_attribute_panel.setCheckable(True)
        menu_view.addAction(self.action_trigger_attribute_panel)

        # adds help menu actions
        self.action_help = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/help.png')), _('Help'), self,
                                         shortcut="F1")
        self.action_help.setText(_("Help"))
        self.action_help.triggered.connect(self.associated_presenter.on_help_triggered)
        menu_help.addAction(self.action_help)

        self.action_about = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/about.png')), _('About'),
                                          self)
        self.action_about.setText(_("About"))
        self.action_about.triggered.connect(self.associated_presenter.on_about_triggered)
        menu_help.addAction(self.action_about)

        # makes the top level actions clickable
        self.addAction(menu_file.menuAction())
        self.addAction(menu_edit.menuAction())
        self.addAction(menu_simulation.menuAction())
        self.addAction(menu_view.menuAction())
        self.addAction(menu_help.menuAction())