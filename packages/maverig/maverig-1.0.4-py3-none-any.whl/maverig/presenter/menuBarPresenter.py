import os
import subprocess
import sys

import dateutil.parser
from PySide import QtGui, QtCore
from PySide.QtCore import QDateTime
from PySide.QtGui import QMessageBox

from maverig.data import config, dataHandler
from maverig.data.config import ConfigKeys
from maverig.models.model import Mode, ProgramMode, fast_deepcopy
from maverig.presenter import abstractPresenter
from maverig.views import dialogs


class MenuBarPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the menu bar. Functionality
    that is concerning the scenario is realized in 'maverig.presenter.scenarioPanelPresenter.ScenarioPanelPresenter'."""

    path = None

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the menu bar presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super(MenuBarPresenter, self).__init__(presenter_manager, model, cfg)

        self.model.language_event += self.on_language
        self.model.elements_event += self.on_elements
        self.model.mode_event += self.on_mode
        self.model.drag_event += self.on_drag
        self.model.program_mode_event += self.on_program_mode
        self.model.selection_event += self.on_selection
        self.model.clipboard_event += self.on_clipboard
        self.model.vid_speed_event += self.on_vid_speed

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_file_new_triggered(self):
        """Discards the current scenario."""
        if self.model.saved_scenario_copy != self.model.tmp_scenario_copy:
            ret = dialogs.inform_dialog()
            if ret == QMessageBox.Save:
                self.on_file_save_triggered()
                self.new_file()
            elif ret == QMessageBox.Discard:
                self.new_file()
        else:
            self.new_file()

    def new_file(self):
        """Clears the current scenario."""
        self.path = None
        self.model.elements.clear()
        self.model.simulators.clear()
        self.model.clipboard_elements.clear()
        self.model.selection.clear()
        self.model.uid.clear()

        self.model.init_history()
        self.model.update_all()

    def on_file_open_triggered(self):
        """Opens a file dialog."""
        if self.model.saved_scenario_copy != self.model.tmp_scenario_copy:
            ret = dialogs.inform_dialog()
            if ret == QMessageBox.Save:
                self.on_file_save_triggered()
                self.open_file()
            elif ret == QMessageBox.Discard:
                self.open_file()
        else:
            self.open_file()

    def open_file(self):
        """Loads a serialized scenario from a chosen file."""
        path, filter = QtGui.QFileDialog.getOpenFileName(self.view, _("Open scenario file"), "", "Maverig (*.mvrg)")
        if path is not '':
            self.model.scenario = config.read_json(path)
            self.presenter_manager.scenario_panel_presenter.zoom_fit()
            self.presenter_manager.status_bar_presenter.success(os.path.basename(path) + config.FILE_OPENED())

            self.path = path
            self.model.init_history()

    def on_file_save_triggered(self):
        """Saves a serialized scenario. If the current scenario isn't saved within a file already a file dialog will
        be opened."""
        if self.path:
            config.write_json(self.path, self.model.scenario)
            self.model.saved_scenario_copy = fast_deepcopy(self.model.scenario)
            self.presenter_manager.status_bar_presenter.success(os.path.basename(self.path) + config.FILE_SAVED())
        else:
            self.on_file_save_as_triggered()

    def on_file_save_as_triggered(self):
        """Opens a file dialog so that the serialized scenario can be saved within a named file."""
        self.path, filter = QtGui.QFileDialog.getSaveFileName(self.view, _("Save scenario file"), "*.mvrg",
                                                              "Maverig (*.mvrg)")
        if self.path:
            config.write_json(self.path, self.model.scenario)
            self.model.saved_scenario_copy = fast_deepcopy(self.model.scenario)
            self.presenter_manager.status_bar_presenter.success(os.path.basename(self.path) + config.FILE_SAVED())
        else:
            self.path = None

    @staticmethod
    def on_quit_triggered():
        """Shuts down the application."""
        sys.exit()

    def on_undo_triggered(self):
        """Undo latest change."""
        self.model.undo()

    def on_redo_triggered(self):
        """Redo latest undone change."""
        self.model.redo()

    def on_cut_triggered(self):
        """Cuts selected elements."""
        self.presenter_manager.scenario_panel_presenter.cut_selected_elements()

    def on_copy_triggered(self):
        """Copies selected elements."""
        self.presenter_manager.scenario_panel_presenter.copy_selected_elements()

    def on_paste_triggered(self):
        """Pastes copied elements and selects them."""
        self.presenter_manager.scenario_panel_presenter.paste_elements()

    def on_delete_triggered(self):
        """Removes selected elements."""
        self.presenter_manager.scenario_panel_presenter.delete_selected_elements()

    def on_select_all_triggered(self):
        """Selects all elements depending on current mode."""
        self.presenter_manager.scenario_panel_presenter.select_all_elements()

    def on_back_to_start_triggered(self):
        """Sets progress slider position to first index."""
        if self.model.program_mode == ProgramMode.simulation_paused:
            self.model.program_mode = ProgramMode.simulation
        self.model.sim_index = 0
        self.model.sim_event.demand()
        self.model.update()

    def on_reduce_speed_triggered(self):
        """Reduces the speed of the progress slider."""
        if self.model.vid_speed < 2000:
            if self.model.vid_speed == 50:
                self.model.vid_speed += 200
            else:
                self.model.vid_speed += 250
            self.change_rel_speed()
            self.model.update()

    def on_run_triggered(self):
        """Starts the simulation and runs or pauses the progress slider. Switches the program mode."""
        if self.model.program_mode == ProgramMode.composition:
            if self.model.validate_scenario():
                self.model.simulation.start()
                self.model.program_mode = ProgramMode.simulation
                self.model.mode = Mode.sim
                self.model.update()
        elif self.model.program_mode == ProgramMode.simulation:
            self.on_pause_triggered()
        elif self.model.program_mode == ProgramMode.simulation_paused:
            self.model.program_mode = ProgramMode.simulation
            self.model.update()

    def on_stop_triggered(self):
        """Stops the simulation and progress slider. Switches to the composition program mode."""
        self.model.simulation.stop()
        self.model.program_mode = ProgramMode.composition
        self.model.mode = Mode.selection
        self.model.update()

    def on_pause_triggered(self):
        """Pauses the progress slider and switches to the simulation paused program mode."""
        self.model.program_mode = ProgramMode.simulation_paused
        self.model.update()

    def on_increase_speed_triggered(self):
        """Increases the speed of the progress slider."""
        if self.model.vid_speed > 0:
            if self.model.vid_speed == 250:
                self.model.vid_speed -= 200
            else:
                self.model.vid_speed -= 250
            self.change_rel_speed()
            self.model.update()

    def on_forward_to_end_triggered(self):
        """Sets progress slider position to last possible index."""
        if self.model.sim_progress == 100:
            self.model.program_mode = ProgramMode.simulation_paused
        self.model.sim_index = len(self.model.sim_timestamps) - 1
        self.model.sim_event.demand()
        self.model.update()

    def on_set_time_triggered(self):
        """Opens a dialog for changing time and speed parameters of the simulation. Sets the start time, the end time,
        the step size and the progress slider speed returned from the dialog."""
        time_dialog = dialogs.SimulationTimeDialog()
        sim_start = self.datetime_to_qdatetime(self.model.sim_start)
        sim_end = self.datetime_to_qdatetime(self.model.sim_end)
        sim_step_size = self.model.sim_step_size
        vid_speed = self.model.vid_speed
        new_start_time, new_end_time, new_sim_step_size, new_vid_speed, new_vid_speed_rel = \
            time_dialog.show(sim_start, sim_end, sim_step_size, vid_speed)
        self.model.sim_start = self.qdatetime_to_datetime(new_start_time)
        self.model.sim_end = self.qdatetime_to_datetime(new_end_time)
        self.model.sim_step_size = new_sim_step_size
        self.model.vid_speed = new_vid_speed
        self.model.vid_speed_rel = new_vid_speed_rel
        self.model.update()

    def on_go_to_triggered(self):
        """Opens a dialog where the user can set the progress slider position to a specific simulation time."""
        current_time = dialogs.go_to_time_dialog(self.model.sim_timestamps, self.model.sim_index)
        self.model.sim_timestamp = self.model.sim_timestamps[current_time]
        self.model.update()

    def on_hand_mode_triggered(self):
        """Toggles the hand mode for shifting the scenario."""
        self.model.switch_modes(Mode.hand, Mode.comp)
        self.model.update()

    def on_selection_mode_triggered(self):
        """Toggles the selection mode for element selection."""
        self.model.switch_modes(Mode.selection, Mode.comp)
        self.model.update()

    def on_raster_mode_triggered(self):
        """Toggles raster mode for element snapping and scenario raster."""
        self.model.raster_mode = self.model.raster_snap_mode = not self.model.raster_mode
        if self.model.program_mode == ProgramMode.composition:
            self.model.comp_raster = self.model.raster_mode
        self.model.update()

    def on_zoom_in_triggered(self):
        """Scales up the scenario."""
        self.presenter_manager.scenario_panel_presenter.zoom(True)

    def on_zoom_out_triggered(self):
        """Scales down the scenario."""
        self.presenter_manager.scenario_panel_presenter.zoom(False)

    def on_zoom_fit_triggered(self):
        """Fits all elements into the view."""
        self.presenter_manager.scenario_panel_presenter.zoom_fit()

    def on_trigger_component_panel(self):
        """Toggles the visibility of the component panel."""
        self.presenter_manager.mode_panel_presenter.on_change_visibility_triggered()

    def on_trigger_property_panel(self):
        """Toggles the visibility of the property panel."""
        self.presenter_manager.property_panel_presenter.on_change_visibility_triggered()

    def on_trigger_console(self):
        """Toggles the visibility of the console panel."""
        self.presenter_manager.console_panel_presenter.on_change_visibility_triggered()

    def on_trigger_status_bar(self):
        """Toggles the visibility of the status bar."""
        self.presenter_manager.status_bar_presenter.on_change_visibility_triggered()

    def on_trigger_progress_bar(self):
        """Toggles the visibility of the progress bar."""
        self.presenter_manager.progress_presenter.on_change_visibility_triggered()

    def on_trigger_attribute_panel(self):
        """Toggles the visibility of the attribute panel."""
        self.presenter_manager.attribute_panel_presenter.on_change_visibility_triggered()

    def on_auto_layout_triggered(self):
        """Triggers scenario redrawing with ForceAtlas2."""
        self.view.action_auto_layout.setDisabled(True)
        self.presenter_manager.scenario_panel_presenter.run_force_layout()

    def on_settings_triggered(self):
        """Opens the settings dialog."""
        self.presenter_manager.settings_presenter.on_change_visibility_triggered()

    @staticmethod
    def on_help_triggered():
        """Opens the User Manual."""
        path = lambda: _('maverig/data/user_guide/User_Manual.pdf')
        user_guide_path = dataHandler.get_normpath(path())
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', user_guide_path))
        elif os.name == 'nt':
            os.startfile(user_guide_path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', user_guide_path))

    @staticmethod
    def on_about_triggered():
        """Opens the about dialog."""
        dialogs.about_dialog()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_language(self):
        """Reacts on language changes. Triggers view reinitialization so that the view adopts the chosen language."""
        self.view.clear()
        self.view.init_ui()

    def on_elements(self):
        """Reacts on changes of the elements count and toggles the state (checked/unchecked/enabled/disabled) of the
        depending actions."""
        if len(self.model.elements) > 0:
            self.view.action_auto_layout.setEnabled(not self.model.force_dragging)
            self.view.action_select_all.setEnabled(True)
            self.view.action_zoom_fit.setEnabled(True)
        else:
            self.view.action_auto_layout.setDisabled(True)
            self.view.action_select_all.setDisabled(True)
            self.view.action_zoom_fit.setDisabled(True)

    def on_mode(self):
        """Reacts on mode changes and toggles the state (checked/unchecked/enabled/disabled) of the depending
        actions."""
        self.view.action_selection_mode.setChecked(self.model.mode == Mode.selection)
        self.view.action_hand_mode.setChecked(self.model.mode == Mode.hand)
        self.view.action_raster_mode.setChecked(self.model.raster_mode)

    def on_drag(self):
        """Reacts if a component is dragged and toggles the state (checked/unchecked/enabled/disabled) of the
        depending actions."""
        if self.model.program_mode == ProgramMode.composition:
            self.view.action_auto_layout.setEnabled(not self.model.selection_dragging
                                                    and not self.model.force_dragging
                                                    and bool(self.model.graph.edges()))

    def on_vid_speed(self):
        """Reacts on changes of the progress slider speed and toggles the state (checked/unchecked/enabled/disabled) of
        the depending actions."""
        if self.model.program_mode != ProgramMode.composition:
            if self.model.vid_speed_rel == 8:
                self.view.action_increase_speed.setDisabled(True)
            elif self.model.vid_speed_rel == 0.5:
                self.view.action_reduce_speed.setDisabled(True)
            else:
                self.view.action_increase_speed.setEnabled(True)
                self.view.action_reduce_speed.setEnabled(True)

    def on_program_mode(self):
        """Reacts on program mode changes and toggles the state (checked/unchecked/enabled/disabled) of the depending
        actions."""
        if self.model.program_mode == ProgramMode.simulation:
            # file actions
            self.view.action_new.setDisabled(True)
            self.view.action_open.setDisabled(True)

            # edit actions
            self.view.action_undo.setDisabled(True)
            self.view.action_redo.setDisabled(True)
            self.view.action_auto_layout.setDisabled(True)
            self.view.action_cut.setDisabled(True)
            self.view.action_copy.setDisabled(True)
            self.view.action_paste.setDisabled(True)
            self.view.action_delete.setDisabled(True)

            # simulation actions
            self.view.action_back_to_start.setEnabled(True)
            self.view.action_reduce_speed.setEnabled(self.model.vid_speed_rel > 0.5)
            self.view.action_increase_speed.setEnabled(self.model.vid_speed_rel < 8)
            self.view.action_forward_to_end.setEnabled(True)
            self.view.action_stop.setEnabled(True)
            self.view.action_run.setDisabled(True)
            self.view.action_pause.setEnabled(self.model.sim_index < self.model.sim_end_index)
            self.view.action_set_time.setDisabled(True)
            self.view.action_go_to_time.setEnabled(True)

            # view actions
            self.view.action_hand_mode.setDisabled(True)
            self.view.action_selection_mode.setDisabled(True)
            self.view.action_raster_mode.setDisabled(True)

            # raster mode
            self.model.raster_mode = False
            self.model.update()

            # simulation panels
            self.view.action_trigger_progress_bar.setEnabled(True)
            self.view.action_trigger_attribute_panel.setEnabled(True)
            self.view.action_trigger_progress_bar.setChecked(
                self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_PROGRESS_BAR_VISIBLE])
            self.view.action_trigger_attribute_panel.setChecked(
                self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_ATTRIBUTE_PANEL_VISIBLE])

            # composition panels
            self.view.action_trigger_component_panel.setDisabled(True)
            self.view.action_trigger_property_panel.setDisabled(True)
            self.view.action_trigger_component_panel.setChecked(False)
            self.view.action_trigger_property_panel.setChecked(False)
            self.view.action_trigger_console.setChecked(
                self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_CONSOLE_PANEL_VISIBLE])
            self.view.action_trigger_status_bar.setChecked(
                self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE])

        elif self.model.program_mode == ProgramMode.composition:
            # file actions
            self.view.action_new.setEnabled(True)
            self.view.action_open.setEnabled(True)

            # edit actions
            self.view.action_undo.setEnabled(True)
            self.view.action_redo.setEnabled(True)
            self.view.action_auto_layout.setEnabled(len(self.model.elements) > 0)
            self.view.action_cut.setEnabled(len(self.model.selection) > 0)
            self.view.action_copy.setEnabled(len(self.model.selection) > 0)
            self.view.action_paste.setEnabled(len(self.model.clipboard_elements) > 0)
            self.view.action_delete.setEnabled(len(self.model.selection) > 0)

            # simulation actions
            self.view.action_back_to_start.setDisabled(True)
            self.view.action_reduce_speed.setDisabled(True)
            self.view.action_increase_speed.setDisabled(True)
            self.view.action_forward_to_end.setDisabled(True)
            self.view.action_run.setEnabled(True)
            self.view.action_stop.setDisabled(True)
            self.view.action_pause.setDisabled(True)
            self.view.action_set_time.setEnabled(True)
            self.view.action_go_to_time.setDisabled(True)

            # view actions
            self.view.action_hand_mode.setEnabled(True)
            self.view.action_selection_mode.setEnabled(True)
            self.view.action_raster_mode.setEnabled(True)

            # raster mode
            self.model.raster_mode = self.model.comp_raster

            # simulation panels
            self.view.action_trigger_progress_bar.setDisabled(True)
            self.view.action_trigger_attribute_panel.setDisabled(True)
            self.view.action_trigger_progress_bar.setChecked(False)
            self.view.action_trigger_attribute_panel.setChecked(False)

            # composition panels
            self.view.action_trigger_component_panel.setEnabled(True)
            self.view.action_trigger_property_panel.setEnabled(True)
            self.view.action_trigger_component_panel.setChecked(
                self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_COMPONENT_PANEL_VISIBLE])
            self.view.action_trigger_property_panel.setChecked(
                self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_PROPERTY_PANEL_VISIBLE])
            self.presenter_manager.scenario_panel_presenter.view.refreshBg()
            self.view.action_trigger_console.setChecked(
                self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_CONSOLE_PANEL_VISIBLE])
            self.view.action_trigger_status_bar.setChecked(
                self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE])

        elif self.model.program_mode == ProgramMode.simulation_paused:
            # actions
            self.view.action_stop.setEnabled(True)
            self.view.action_run.setEnabled(self.model.sim_index < self.model.sim_end_index)
            self.view.action_pause.setDisabled(True)

    def on_selection(self):
        """Reacts on selection changes and toggles the state (checked/unchecked/enabled/disabled) of the depending
        actions."""
        if self.model.program_mode == ProgramMode.composition:
            if len(self.model.selection) > 0:
                self.view.action_cut.setEnabled(True)
                self.view.action_copy.setEnabled(True)
                self.view.action_delete.setEnabled(True)
            else:
                self.view.action_cut.setDisabled(True)
                self.view.action_copy.setDisabled(True)
                self.view.action_delete.setDisabled(True)

    def on_clipboard(self):
        """Reacts on clipboard changes and toggles the state (checked/unchecked/enabled/disabled) of the depending
        actions."""
        if self.model.program_mode == ProgramMode.composition:
            if len(self.model.clipboard_elements) > 0:
                self.view.action_paste.setEnabled(True)
            else:
                self.view.action_paste.setDisabled(True)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Helper -----------------------------------------------------------------------------------------------------------

    @staticmethod
    def datetime_to_qdatetime(date_time):
        return QDateTime.fromString(date_time.isoformat(), QtCore.Qt.ISODate)

    @staticmethod
    def qdatetime_to_datetime(qdatetime):
        return dateutil.parser.parse(qdatetime.toString(QtCore.Qt.ISODate))

    def change_rel_speed(self):
        if self.model.vid_speed == 50:
            self.model.vid_speed_rel = 8
        elif self.model.vid_speed == 250:
            self.model.vid_speed_rel = 4
        elif self.model.vid_speed == 500:
            self.model.vid_speed_rel = 2
        elif self.model.vid_speed == 750:
            self.model.vid_speed_rel = 1.5
        elif self.model.vid_speed == 1000:
            self.model.vid_speed_rel = 1
        elif self.model.vid_speed == 1250:
            self.model.vid_speed_rel = 0.875
        elif self.model.vid_speed == 1500:
            self.model.vid_speed_rel = 0.75
        elif self.model.vid_speed == 1750:
            self.model.vid_speed_rel = 0.625
        elif self.model.vid_speed == 2000:
            self.model.vid_speed_rel = 0.5