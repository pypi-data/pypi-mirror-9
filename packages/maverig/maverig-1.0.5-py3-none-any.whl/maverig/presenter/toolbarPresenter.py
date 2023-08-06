from PySide import QtGui

from maverig.data import dataHandler
from maverig.models.model import ProgramMode
from maverig.presenter import abstractPresenter


class ToolbarPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for toolbar. Events that are fired
    by the toolbar view are mapped to the menu bar presenter because all functionality of the toolbar is covered by the
    menu bar. Code changes can be realized at one place in this way.
    """

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the toolbar presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super().__init__(presenter_manager, model, cfg)

        self.model.language_event += self.on_language
        self.model.selection_event += self.on_selection
        self.model.drag_event += self.on_drag
        self.model.elements_event += self.on_elements
        self.model.sim_event += self.on_sim
        self.model.program_mode_event += self.on_program_mode
        self.model.vid_speed_event += self.on_vid_speed

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_file_open_triggered(self):
        """Opens a file dialog."""
        self.presenter_manager.menu_bar_presenter.on_file_open_triggered()

    def on_file_save_triggered(self):
        """Saves a serialized scenario. If the current scenario isn't saved within a file already a file dialog will
        be opened."""
        self.presenter_manager.menu_bar_presenter.on_file_save_triggered()

    def on_back_to_start_triggered(self):
        """Sets progress slider position to first index."""
        self.presenter_manager.menu_bar_presenter.on_back_to_start_triggered()

    def on_reduce_speed_triggered(self):
        """Reduces the speed of the progress slider."""
        self.presenter_manager.menu_bar_presenter.on_reduce_speed_triggered()

    def on_run_triggered(self):
        """Starts the simulation and runs or pauses the progress slider. Switches the program mode."""
        self.presenter_manager.menu_bar_presenter.on_run_triggered()

    def on_stop_triggered(self):
        """Stops the simulation and progress slider. Switches to the composition program mode."""
        self.presenter_manager.menu_bar_presenter.on_stop_triggered()

    def on_increase_speed_triggered(self):
        """Increases the speed of the progress slider."""
        self.presenter_manager.menu_bar_presenter.on_increase_speed_triggered()

    def on_forward_to_end_triggered(self):
        """Sets progress slider position to last possible index."""
        self.presenter_manager.menu_bar_presenter.on_forward_to_end_triggered()

    def on_zoom_in_triggered(self):
        """Scales up the scenario."""
        self.presenter_manager.menu_bar_presenter.on_zoom_in_triggered()

    def on_zoom_out_triggered(self):
        """Scales down the scenario."""
        self.presenter_manager.menu_bar_presenter.on_zoom_out_triggered()

    def on_zoom_fit_triggered(self):
        """Fits all elements into the view."""
        self.presenter_manager.menu_bar_presenter.on_zoom_fit_triggered()

    def on_delete_triggered(self):
        """Removes selected elements."""
        self.presenter_manager.menu_bar_presenter.on_delete_triggered()

    def on_settings_triggered(self):
        """Opens the settings dialog."""
        self.presenter_manager.menu_bar_presenter.on_settings_triggered()

    def on_auto_layout_triggered(self):
        """Triggers scenario redrawing with ForceAtlas2."""
        self.view.action_auto_layout.setDisabled(True)
        self.presenter_manager.menu_bar_presenter.on_auto_layout_triggered()

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
            self.view.action_zoom_fit.setEnabled(True)
        else:
            self.view.action_auto_layout.setDisabled(True)
            self.view.action_zoom_fit.setDisabled(True)

    def on_selection(self):
        """Reacts on selection changes and toggles the state (checked/unchecked/enabled/disabled) of the depending
        actions."""
        if self.model.program_mode == ProgramMode.composition:
            if len(self.model.selection) > 0:
                self.view.action_delete.setEnabled(True)
            else:
                self.view.action_delete.setDisabled(True)

    def on_drag(self):
        """Reacts if a component is dragged and toggles the state (checked/unchecked/enabled/disabled) of the
        depending actions."""
        if self.model.program_mode == ProgramMode.composition:
            self.view.action_auto_layout.setEnabled(not self.model.selection_dragging
                                                    and not self.model.force_dragging
                                                    and bool(self.model.graph.edges()))

    def on_sim(self):
        """Reacts on changes of the simulation time and speed parameters and toggles the state
        (checked/unchecked/enabled/disabled) of the depending actions."""
        if self.model.program_mode != ProgramMode.composition:
            self.view.action_run.setEnabled(self.model.sim_index != self.model.sim_end_index)

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
        if self.model.program_mode == ProgramMode.composition:
            # file actions
            self.view.action_open.setEnabled(True)

            # playback actions
            self.view.action_back_to_start.setDisabled(True)
            self.view.action_reduce_speed.setDisabled(True)
            self.view.action_increase_speed.setDisabled(True)
            self.view.action_forward_to_end.setDisabled(True)
            self.view.action_stop.setDisabled(True)
            self.view.action_run.setEnabled(True)

            self.view.action_run.setIcon(QtGui.QIcon(dataHandler.get_icon('toolbar/vid_start.png')))
            self.view.action_run.setToolTip(_('Run'))

            # edit actions
            self.view.action_delete.setEnabled(len(self.model.selection) > 0)
            self.view.action_auto_layout.setEnabled(len(self.model.elements) > 0)

        elif self.model.program_mode == ProgramMode.simulation:
            # file actions
            self.view.action_open.setDisabled(True)

            # playback actions
            self.view.action_back_to_start.setEnabled(True)
            self.view.action_reduce_speed.setEnabled(self.model.vid_speed_rel > 0.5)
            self.view.action_increase_speed.setEnabled(self.model.vid_speed_rel < 8)
            self.view.action_forward_to_end.setEnabled(True)
            self.view.action_stop.setEnabled(True)
            self.view.action_run.setEnabled(self.model.sim_index < self.model.sim_end_index)

            self.view.action_run.setIcon(QtGui.QIcon(dataHandler.get_icon('toolbar/vid_pause.png')))
            self.view.action_run.setToolTip(_('Pause'))

            # edit actions
            self.view.action_delete.setDisabled(True)
            self.view.action_auto_layout.setDisabled(True)

        elif self.model.program_mode == ProgramMode.simulation_paused:
            # playback actions
            self.view.action_stop.setEnabled(True)
            self.view.action_run.setEnabled(self.model.sim_index < self.model.sim_end_index)

            self.view.action_run.setIcon(QtGui.QIcon(dataHandler.get_icon('toolbar/vid_start.png')))
            self.view.action_run.setToolTip(_('Run'))