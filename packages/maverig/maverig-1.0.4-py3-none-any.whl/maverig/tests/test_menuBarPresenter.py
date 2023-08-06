import gettext
import locale
from datetime import datetime
import sys
from unittest import TestCase

from PySide import QtCore, QtGui

from maverig.models.model import Mode, ProgramMode, Model
from maverig.presenter.presenterManager import PresenterManager
from maverig.data import dataHandler, config
from maverig.views.attributePanelView import AttributePanelView
from maverig.views.modePanelView import ModePanelView
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.menuBarView import MenuBarView
from maverig.views.progressView import ProgressView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.settingsView import SettingsView
from maverig.views.statusBarView import StatusBarView
from maverig.views.toolbarView import ToolbarView
from maverig.data.config import ConfigKeys

try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestMenusBarPresenter(TestCase):
    def setUp(self):
        self.model = Model()
        cfg = config.read_config()
        self.presenter_manager = PresenterManager(self.model, cfg)
        self.menu_bar_view = MenuBarView()

        # Install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        settings_view = SettingsView()
        attribute_panel_view = AttributePanelView()
        property_panel_view = PropertyPanelView()
        tool_bar_view = ToolbarView()
        scenario_panel_view = ScenarioPanelView()
        status_bar_view = StatusBarView()
        mode_panel_view = ModePanelView()
        progress_view = ProgressView()
        console_panel_view = ConsolePanelView()

        self.menu_bar_presenter = self.presenter_manager.menu_bar_presenter

        self.presenter_manager.settings_presenter.view = settings_view
        self.presenter_manager.attribute_panel_presenter.view = attribute_panel_view
        self.presenter_manager.menu_bar_presenter.view = self.menu_bar_view
        self.presenter_manager.property_panel_presenter.view = property_panel_view
        self.presenter_manager.toolbar_presenter.view = tool_bar_view
        self.presenter_manager.scenario_panel_presenter.view = scenario_panel_view
        self.presenter_manager.status_bar_presenter.view = status_bar_view
        self.presenter_manager.mode_panel_presenter.view = mode_panel_view
        self.presenter_manager.progress_presenter.view = progress_view
        self.presenter_manager.console_panel_presenter.view = console_panel_view

        attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter
        self.menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        tool_bar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        scenario_panel_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        mode_panel_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        progress_view.associated_presenter = self.presenter_manager.progress_presenter
        console_panel_view.associated_presenter = self.presenter_manager.console_panel_presenter
        settings_view.associated_presenter = self.presenter_manager.settings_presenter

        attribute_panel_view.init_ui()
        self.menu_bar_view.init_ui()
        property_panel_view.init_ui()
        tool_bar_view.init_ui()
        scenario_panel_view.init_ui()
        status_bar_view.init_ui()
        mode_panel_view.init_ui()
        progress_view.init_ui()
        console_panel_view.init_ui()

    def test_on_back_to_start_triggered(self):
        """Set simulated progress-visualisation to 0."""
        self.model.program_mode = ProgramMode.simulation_paused
        self.menu_bar_presenter.on_back_to_start_triggered()

        assert self.model.program_mode == ProgramMode.simulation

    def test_on_reduce_speed_triggered(self):
        """Set simulated progress-visualisation slower in speed."""
        self.model.vid_speed = 1000
        self.menu_bar_presenter.on_reduce_speed_triggered()

        assert self.model.vid_speed == 1250

        self.model.vid_speed = 2000
        self.menu_bar_presenter.on_reduce_speed_triggered()

        assert self.model.vid_speed == 2000

    def test_on_run_triggered(self):
        """Runs the simulation."""
        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))
        self.model.program_mode = ProgramMode.composition
        self.menu_bar_presenter.on_run_triggered()

        assert self.model.program_mode == ProgramMode.simulation

        self.model.program_mode = ProgramMode.simulation
        self.menu_bar_presenter.on_run_triggered()

        assert self.model.program_mode == ProgramMode.simulation_paused

        self.menu_bar_presenter.on_run_triggered()

        assert self.model.program_mode == ProgramMode.simulation

        self.menu_bar_presenter.on_stop_triggered()

    def test_on_stop_triggered(self):
        """Stops the simulation."""
        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))
        self.model.program_mode = ProgramMode.composition
        self.menu_bar_presenter.on_run_triggered()

        assert self.model.program_mode == ProgramMode.simulation

        self.menu_bar_presenter.on_stop_triggered()

        assert self.model.program_mode == ProgramMode.composition
        assert self.model.mode == Mode.selection

    def test_on_pause_triggered(self):
        """Pauses the simulation."""
        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))
        self.model.program_mode = ProgramMode.composition
        self.menu_bar_presenter.on_run_triggered()

        assert self.model.program_mode == ProgramMode.simulation

        self.menu_bar_presenter.on_pause_triggered()

        assert self.model.program_mode == ProgramMode.simulation_paused

        self.menu_bar_presenter.on_stop_triggered()

    def test_on_increase_speed_triggered(self):
        """Set simulated progress-visualisation faster in speed."""
        self.model.vid_speed = 1000
        self.menu_bar_presenter.on_increase_speed_triggered()

        assert self.model.vid_speed == 750

    def test_on_forward_to_end_triggered(self):
        """Set simulated progress-visualisation to the end of simulation."""
        self.model.sim_progress = 100
        self.menu_bar_presenter.on_forward_to_end_triggered()

        assert self.model.program_mode == ProgramMode.simulation_paused
        assert self.model.sim_index == len(self.model.sim_timestamps) - 1

    def test_on_set_time_triggered(self):
        """Sets the start time and the duration of the simulation via a dialog."""
        sim_start = self.menu_bar_presenter.datetime_to_qdatetime(self.model.sim_start)
        sim_end = self.menu_bar_presenter.datetime_to_qdatetime(self.model.sim_end)
        sim_step_size = self.model.sim_step_size
        vid_speed = self.model.vid_speed
        vid_speed_rel = self.model.vid_speed_rel

        new_start_time = QtCore.QDateTime(2014, 10, 23, 18, 28, 21, 134, 0)
        new_end_time = QtCore.QDateTime(2014, 10, 26, 18, 28, 21, 134, 0)
        new_sim_step_size = 3600
        new_vid_speed = self.model.vid_speed-250
        new_vid_speed_rel = self.menu_bar_presenter.change_rel_speed()

        self.menu_bar_presenter.model.sim_start = self.menu_bar_presenter.qdatetime_to_datetime(new_start_time)
        self.menu_bar_presenter.model.sim_end = self.menu_bar_presenter.qdatetime_to_datetime(new_end_time)
        self.menu_bar_presenter.model.sim_step_size = new_sim_step_size
        self.menu_bar_presenter.model.vid_speed = new_vid_speed
        self.menu_bar_presenter.model.vid_speed_rel = new_vid_speed_rel

        assert sim_start != self.menu_bar_presenter.model.sim_start
        assert sim_end != self.menu_bar_presenter.model.sim_end
        assert sim_step_size != self.menu_bar_presenter.model.sim_step_size
        assert vid_speed != self.menu_bar_presenter.model.vid_speed
        assert vid_speed_rel != self.menu_bar_presenter.model.vid_speed_rel

    def test_on_go_to_triggered(self):
        """Go to an specific simulation time position"""
        self.model.sim_timestamps.append(datetime(2014, 10, 22, 4, 30, 00))
        self.model.sim_timestamps.append(datetime(2014, 10, 22, 4, 40, 00))
        self.model.sim_timestamps.append(datetime(2014, 10, 22, 4, 50, 00))
        current_time = 1
        self.model.sim_timestamp = self.model.sim_timestamps[current_time]

        assert self.model.sim_timestamp == datetime(2014, 10, 22, 4, 40, 00)

    def test_on_hand_mode_triggered(self):
        """Toggles the hand mode for shifting the scenario."""
        self.model.mode = Mode.comp
        self.menu_bar_presenter.on_hand_mode_triggered()
        assert self.menu_bar_presenter.model.mode == Mode.hand

    def test_on_selection_mode_triggered(self):
        """Toggles the hand mode for element selection."""
        self.model.mode = Mode.comp
        self.menu_bar_presenter.on_selection_mode_triggered()
        assert self.menu_bar_presenter.model.mode == Mode.selection

    def test_on_raster_mode_triggered(self):
        """ Toggles raster mode for element snapping """
        self.model.raster_mode = False
        self.model.raster_snap_mode = True
        self.model.program_mode = ProgramMode.composition
        self.menu_bar_presenter.on_raster_mode_triggered()

        assert self.model.comp_raster

    def test_on_elements(self):
        """Reacts on changes of the elements count and toggles the state (checked/unchecked/enabled/disabled) of the
        depending actions."""
        self.menu_bar_presenter.on_elements()

        assert not self.menu_bar_view.action_select_all.isEnabled()
        assert not self.menu_bar_view.action_auto_layout.isEnabled()
        assert not self.menu_bar_view.action_zoom_fit.isEnabled()

        self.model.create_element('PyPower.RefBus', QtCore.QPointF(200.0, 150.0))
        self.menu_bar_presenter.on_elements()

        assert self.menu_bar_view.action_select_all.isEnabled()
        assert self.menu_bar_view.action_auto_layout.isEnabled()
        assert self.menu_bar_view.action_zoom_fit.isEnabled()

    def test_on_mode(self):
        """Reacts on model changes of the current mode and toggles the checked state of the selection mode and hand
        mode."""
        self.model.mode = Mode.selection
        self.menu_bar_presenter.on_mode()

        assert self.menu_bar_view.action_selection_mode.isChecked()
        assert not self.menu_bar_view.action_hand_mode.isChecked()

        self.menu_bar_presenter.model.mode = Mode.hand
        self.menu_bar_presenter.on_mode()

        assert not self.menu_bar_view.action_selection_mode.isChecked()
        assert self.menu_bar_view.action_hand_mode.isChecked()

    def test_on_drag(self):
        self.model.selection_dragging = True
        self.model.force_dragging = True
        self.model.graph.edges().clear()
        self.model.program_mode = ProgramMode.composition
        self.menu_bar_presenter.on_drag()

        assert not self.menu_bar_view.action_auto_layout.isEnabled()

    def test_on_vid_speed(self):
        self.model.program_mode = ProgramMode.simulation
        self.model.vid_speed_rel = 8
        self.menu_bar_presenter.on_vid_speed()

        assert not self.menu_bar_view.action_increase_speed.isEnabled()

        self.model.vid_speed_rel = 0.5
        self.menu_bar_presenter.on_vid_speed()

        assert not self.menu_bar_view.action_reduce_speed.isEnabled()

        self.model.vid_speed_rel = 5
        self.menu_bar_presenter.on_vid_speed()

        assert self.menu_bar_view.action_increase_speed.isEnabled()
        assert self.menu_bar_view.action_reduce_speed.isEnabled()

    def test_on_program_mode(self):
        """Reacts on model changes of the current program mode and adjust the ui to reflect the program mode
        composition, simulation or simulation paused."""
        self.model.program_mode = ProgramMode.simulation
        self.menu_bar_presenter.on_program_mode()

        assert not self.menu_bar_view.action_undo.isEnabled()
        assert not self.menu_bar_view.action_redo.isEnabled()
        assert not self.menu_bar_view.action_auto_layout.isEnabled()
        assert not self.menu_bar_view.action_cut.isEnabled()
        assert not self.menu_bar_view.action_copy.isEnabled()
        assert not self.menu_bar_view.action_paste.isEnabled()
        assert not self.menu_bar_view.action_delete.isEnabled()
        assert self.menu_bar_view.action_back_to_start.isEnabled()
        assert self.menu_bar_view.action_forward_to_end.isEnabled()
        assert self.menu_bar_view.action_stop.isEnabled()
        assert not self.menu_bar_view.action_set_time.isEnabled()
        assert self.menu_bar_view.action_go_to_time.isEnabled()

        self.model.program_mode = ProgramMode.composition
        self.menu_bar_presenter.on_program_mode()

        assert self.menu_bar_view.action_new.isEnabled()
        assert self.menu_bar_view.action_open.isEnabled()
        assert self.menu_bar_view.action_undo.isEnabled()
        assert self.menu_bar_view.action_redo.isEnabled()
        assert not self.menu_bar_view.action_back_to_start.isEnabled()
        assert not self.menu_bar_view.action_reduce_speed.isEnabled()
        assert not self.menu_bar_view.action_increase_speed.isEnabled()
        assert not self.menu_bar_view.action_forward_to_end.isEnabled()
        assert self.menu_bar_view.action_run.isEnabled()
        assert not self.menu_bar_view.action_stop.isEnabled()
        assert not self.menu_bar_view.action_pause.isEnabled()
        assert self.menu_bar_view.action_set_time.isEnabled()
        assert not self.menu_bar_view.action_go_to_time.isEnabled()

        self.model.program_mode = ProgramMode.simulation_paused
        self.menu_bar_presenter.on_program_mode()
        assert self.menu_bar_view.action_stop.isEnabled()
        assert not self.menu_bar_view.action_pause.isEnabled()

    def test_on_selection(self):
        """Reacts on model changes of the current selection and toggles the state of the cut, copy and delete
        actions."""

        elem_id = self.model.create_element('PyPower.RefBus', QtCore.QPointF(100.0, 200.0))
        self.model.set_selected(elem_id, True)
        self.menu_bar_presenter.on_selection()

        assert self.menu_bar_view.action_copy.isEnabled()
        assert self.menu_bar_view.action_cut.isEnabled()
        assert self.menu_bar_view.action_delete.isEnabled()

        self.model.set_selected(elem_id, False)
        self.menu_bar_presenter.on_selection()

        assert not self.menu_bar_view.action_copy.isEnabled()
        assert not self.menu_bar_view.action_cut.isEnabled()
        assert not self.menu_bar_view.action_delete.isEnabled()

    def test_on_clipboard(self):
        """Reacts on model changes of the clipboard and toggles the state of the paste action."""
        self.menu_bar_presenter.on_clipboard()

        assert not self.menu_bar_view.action_paste.isEnabled()

        elem_id = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200.0, 150.0))
        self.model.clipboard_elements[elem_id] = 1
        self.menu_bar_presenter.on_clipboard()

        assert len(self.model.clipboard_elements) > 0
        assert self.menu_bar_view.action_paste.isEnabled()

    def test_change_rel_speed(self):

        self.model.vid_speed = 50
        self.model.update()

        for i in range(8):
            old_rel = self.model.vid_speed_rel
            self.menu_bar_presenter.on_reduce_speed_triggered()
            self.model.update()
            assert not old_rel is self.model.vid_speed_rel