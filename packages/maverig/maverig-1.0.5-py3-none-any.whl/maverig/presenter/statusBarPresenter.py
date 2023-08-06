from maverig.data import config
from maverig.data.config import ConfigKeys
from maverig.models.model import Mode, ProgramMode
from maverig.presenter import abstractPresenter


class StatusBarPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the status bar."""

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the status bar presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super(StatusBarPresenter, self).__init__(presenter_manager, model, cfg)

        self.model.language_event += self.on_language
        self.model.vid_speed_event += self.on_vid_speed_event
        self.model.drag_event += self.on_drag
        self.model.mode_event += self.on_mode
        self.model.program_mode_event += self.on_program_mode

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_change_visibility_triggered(self):
        """Toggles the visibility of the status bar. Saves the visibility state in the config."""
        self.view.setHidden(not self.view.isHidden())
        self.presenter_manager.menu_bar_presenter.view.action_trigger_status_bar.setChecked(not self.view.isHidden())
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE] = not self.view.isHidden()
        config.write_config(self.cfg)
        self.model.settings_event.demand()
        self.model.update()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_language(self):
        """Reacts on language changes. Triggers view reinitialization so that the view adopts the chosen language."""
        self.view.init_ui()

    def on_drag(self):
        """Reacts if an element is dragged. Displays information that dragging is active currently."""
        if self.model.force_dragging:
            self.info(config.ACTIVATED_AUTO_LAYOUT_MODE())
        else:
            self.on_mode()

    def on_mode(self):
        """Reacts on mode changes. Displays the chosen mode in the status bar."""
        if self.model.mode == Mode.hand:
            self.info(config.ACTIVATED_HAND_MODE())
        elif self.model.mode == Mode.selection:
            self.info(config.ACTIVATED_SELECTION_MODE())
        elif self.model.mode == Mode.comp:
            self.info(config.ACTIVATED_COMPONENT_MODE())

    def on_vid_speed_event(self):
        """Reacts on changes of the progress slider speed. Displays the current speed in the status bar."""
        if self.model.program_mode == ProgramMode.simulation:
            self.info((config.ACTIVATED_SIMULATION_MODE() + config.SEPARATOR() + config.SIMULATION_SPEED() +
                       config.SEPARATOR() + str(self.model.vid_speed_rel) + "x"))
        elif self.model.program_mode == ProgramMode.simulation_paused:
            self.info((config.ACTIVATED_SIMULATION_MODE() + config.SEPARATOR() + config.SIMULATION_SPEED() +
                       config.SEPARATOR() + str(
                self.model.vid_speed_rel) + "x" + config.SEPARATOR() + config.SIMULATION_PAUSED()))

    def on_program_mode(self):
        """Reacts on program mode changes. The status bar is visible in every program mode if the user didn't hide
        it."""
        if self.model.program_mode == ProgramMode.composition:
            self.on_mode()
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE])
        elif self.model.program_mode == ProgramMode.simulation:
            self.info((config.ACTIVATED_SIMULATION_MODE() + config.SEPARATOR() + config.SIMULATION_SPEED() +
                       config.SEPARATOR() + str(self.model.vid_speed_rel) + "x"))
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE])
        else:
            self.info((config.ACTIVATED_SIMULATION_MODE() + config.SEPARATOR() + config.SIMULATION_SPEED() +
                       config.SEPARATOR() + str(
                self.model.vid_speed_rel) + "x" + config.SEPARATOR() + config.SIMULATION_PAUSED()))
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE])

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Helper -----------------------------------------------------------------------------------------------------------

    def error(self, message):
        """Sets the given message in the status bar and applies a red background to the status bar."""
        self.view.status_message.setText(message)
        self.view.status_message.setStyleSheet("padding: 0px; color: #FFFFFF")
        self.view.setStyleSheet("padding: -5px; background-color: #B52424")

    def info(self, message):
        """Sets the given message in the status bar and applies a blue background to the status bar.."""
        self.view.status_message.setText(message)
        self.view.status_message.setStyleSheet("padding: 0px; color: #FFFFFF")
        self.view.setStyleSheet("padding: -5px; background-color: #266580")

    def success(self, message):
        """Sets the given message in the status bar and applies a green background to the status bar.."""
        self.view.status_message.setText(message)
        self.view.status_message.setStyleSheet("padding: 0px; color: #FFFFFF")
        self.view.setStyleSheet("padding: -5px; background-color: #5E8227")

    def reset(self):
        """Resets the status bar."""
        self.view.status_message.setText("Nothing to report.")
        self.view.status_message.setStyleSheet("padding: 0px; border: none")
        self.view.setStyleSheet("padding: -5px; border: 1px solid #484848")