from PySide import QtCore

from maverig.presenter import abstractPresenter
from maverig.data import config
from maverig.data.config import ConfigKeys
from maverig.models.model import ProgramMode


class ProgressPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the progress bar."""

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the progress bar presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super(ProgressPresenter, self).__init__(presenter_manager, model, cfg)

        self.model.language_event += self.on_language
        self.model.progress_event += self.on_progress
        self.model.sim_event += self.on_sim
        self.model.program_mode_event += self.on_program_mode
        self.model.vid_speed_event += self.on_vid_speed

        self.date_format = True
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_iteration)

        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self.run_refresh)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_language(self):
        """Reacts on language changes. Triggers view reinitialization so that the view adopts the chosen language."""
        self.view.translate()

    def on_slider_moved(self, position):
        """Sets simulation data index to current slider position. Keeps slider position valid if the mosaik simulation
        progress isn't as far as the position. The model performs lazy updates on the UI through the refresh_timer to
        prevent application from speed and graph animation issues.
        """
        self.model.sim_index = position

        # move slider back if position has not been simulated by mosaik yet
        if self.model.sim_index < position:
            self.view.slider.blockSignals(True)
            self.view.slider.setValue(self.model.sim_index)
            self.view.slider.blockSignals(False)

    def on_change_visibility_triggered(self):
        """Toggles the visibility of the progress bar. Saves the visibility state in the config."""
        self.view.setHidden(not self.view.isHidden())
        self.presenter_manager.menu_bar_presenter.view.action_trigger_progress_bar.setChecked(not self.view.isHidden())
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_PROGRESS_BAR_VISIBLE] = not self.view.isHidden()
        config.write_config(self.cfg)
        self.model.settings_event.demand()
        self.model.update()

    def on_change_dateformat(self):
        """Toggles displaying of the date."""
        self.on_screen_dateformat()
        if self.date_format:
            self.date_format = False
        else:
            self.date_format = True

    def on_screen_dateformat(self):
        """Reacts on changes of the date display. Displays the date as calendar date or as countdown."""
        if self.date_format:
            end_date = str(self.model.sim_end)
            end_date = end_date.split(" ")
            start_date = str(self.model.sim_timestamp)
            start_date = start_date.split(" ")
            self.view.end_date.setText(end_date[0])
            self.view.end_time.setText(end_date[1])
            self.view.actual_date.setText(start_date[0])
            self.view.actual_time.setText(start_date[1])
        else:
            end_date = str(self.model.sim_end - self.model.sim_timestamp)
            end_date = end_date.split(",")
            start_date = str(self.model.sim_timestamp - self.model.sim_start)
            start_date = start_date.split(",")
            self.view.end_date.setText("- " + end_date[0])
            self.view.end_time.setText(end_date[1])
            if len(start_date) > 1:
                self.view.actual_date.setText(start_date[0])
                self.view.actual_time.setText(start_date[1])
            else:
                self.view.actual_date.setText("0 days")
                self.view.actual_time.setText(start_date[0])

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_progress(self):
        """Applies the current mosaik simulation progress to the progress bar."""
        self.view.progress.setValue(self.model.sim_progress)

        if self.model.sim_progress >= 100:
            self.presenter_manager.status_bar_presenter.success(config.SIMULATION_COMPLETED())
            self.model.output_event("Progress: 100.00%", new_line=False)
            self.model.output_event("Simulation finished.", new_line=True)

    def on_sim(self):
        """Reacts on simulation data index changes. Updates the slider position and the date."""
        if self.view.slider.maximum() != self.model.sim_end_index:
            self.view.slider.setMaximum(self.model.sim_end_index)

        self.view.slider.blockSignals(True)
        self.view.slider.setValue(self.model.sim_index)
        self.view.slider.blockSignals(False)

        self.on_screen_dateformat()

        if self.model.program_mode != ProgramMode.composition:
            if self.model.sim_index == self.model.sim_end_index:
                self.model.program_mode = ProgramMode.simulation_paused
                self.model.update()

    def on_vid_speed(self):
        """Reacts on changes of the progress slider speed. Stops und starts the progress slider to adopt new speed."""
        if self.timer.isActive():
            self.stop_slider()
            self.run_slider()

    def on_program_mode(self):
        """Reacts on program mode changes. In the composition program mode the progress bar is hided while the progress
        bar is visible in the simulation program mode if the user didn't hide it. In addition the progress slider and
        the progress bar are set back if application switches to the composition program mode."""
        if self.model.program_mode == ProgramMode.composition:
            self.view.hide()
            self.stop_slider()
            self.refresh_timer.stop()
            self.view.progress.setValue(0)
            self.view.slider.setValue(0)
        elif self.model.program_mode == ProgramMode.simulation:
            self.refresh_timer.start(40)
            self.run_slider()
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_PROGRESS_BAR_VISIBLE])
        elif self.model.program_mode == ProgramMode.simulation_paused:
            self.refresh_timer.start(40)
            self.stop_slider()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Helper -----------------------------------------------------------------------------------------------------------

    def run_slider(self):
        """Starts the progress slider."""
        self.timer.start(self.model.vid_speed)

    def stop_slider(self):
        """Stops the progress slider."""
        self.timer.stop()

    def run_iteration(self):
        """Updates the simulation data index which is responsible for moving the progress slider."""
        self.model.sim_index += 1

    def run_refresh(self):
        """Connected to timer which is responsible for model updates."""
        self.model.update()