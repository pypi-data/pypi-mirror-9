from PySide import QtGui

from maverig.data import config
from maverig.data.config import ConfigKeys
from maverig.presenter import abstractPresenter
from maverig.models.model import ProgramMode


class ConsolePanelPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the console panel."""

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the console panel presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super(ConsolePanelPresenter, self).__init__(presenter_manager, model, cfg)

        self.model.language_event += self.on_language
        self.model.output_event += self.on_output
        self.model.program_mode_event += self.on_program_mode

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_change_visibility_triggered(self):
        """Toggles the visibility of the console panel. Saves the visibility state in the config."""
        self.view.setHidden(not self.view.isHidden())
        self.presenter_manager.menu_bar_presenter.view.action_trigger_console.setChecked(not self.view.isHidden())
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_CONSOLE_PANEL_VISIBLE] = not self.view.isHidden()
        config.write_config(self.cfg)
        self.model.settings_event.demand()
        self.model.update()

    def on_console_clear_triggered(self):
        """Clears the console output."""
        self.view.txt_edit_console.clear()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_language(self):
        """Reacts on language changes. Triggers view reinitialization so that the view adopts the chosen language."""
        self.view.translate()

    def on_program_mode(self):
        """Reacts on program mode changes. The console panel is visible in every program mode if the user didn't hide
        it."""
        if self.model.program_mode == ProgramMode.composition:
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_CONSOLE_PANEL_VISIBLE])
        elif self.model.program_mode == ProgramMode.simulation:
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_CONSOLE_PANEL_VISIBLE])

    def on_output(self, output, new_line=True):
        """Appends the given output to the console output."""
        if self.view.txt_edit_console:
            txt = self.view.txt_edit_console

            txt.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
            if new_line and not txt.document().isEmpty():
                txt.textCursor().insertText('\n')

            else:
                txt.moveCursor(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)  # override last line
            txt.textCursor().insertText(output)

            txt.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)  # make last line visible