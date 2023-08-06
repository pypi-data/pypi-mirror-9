import gettext

from maverig.data import config
from maverig.data.config import ConfigKeys
from maverig.presenter import abstractPresenter
from maverig.data.settings.settings import Settings, SettingTypes
from maverig.data import dataHandler


class SettingsPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the settings dialog."""

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the settings dialog presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super(SettingsPresenter, self).__init__(presenter_manager, model, cfg)

        self.do_change_language = False
        self.install_language(False)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_change_visibility_triggered(self):
        """Shows the settings dialog."""
        self.view.show(self.cfg)

    def on_language_changed(self):
        """Sets flag 'do_change_language' to true if the language has been changed. The flag is used when the presenter
        applies the settings."""
        self.do_change_language = True

    def install_language(self, do_update=True):
        """Sets chosen language if it is changed by user. This is handled separately to prevent handling of unnecessary
        events in whole application if the language hasn't been changed."""
        locale_path = dataHandler.get_lang_path()
        self.model.language = self.cfg[ConfigKeys.GENERAL_SETTINGS][ConfigKeys.LANGUAGE]
        gettext.translation(self.model.language, locale_path, [self.model.language]).install()

        self.model.elements_event.demand()
        self.model.selection_event.demand()
        self.model.mode_event.demand()
        self.model.program_mode_event.demand()
        self.model.clipboard_event.demand()

        if do_update:
            self.model.update()

    def apply_settings(self):
        """Triggers applying of settings."""
        for tab in Settings.tabs:
            for setting in tab.settings:
                self.apply_setting(tab, setting, False)

        config.write_config(self.cfg)

        if self.do_change_language:
            self.do_change_language = False
            self.install_language(False)

        self.model.update()

    def apply_setting(self, tab, setting, do_update=True):
        """Applies the given setting."""
        if not setting:
            return

        if setting.type == SettingTypes.CHECK_BOX:
            self.cfg[tab.key][setting.key] = setting.ui_widget.isChecked()
            self.apply_setting(tab, setting.input, False)
            self.apply_setting(tab, setting.combo_box, False)

        elif setting.type == SettingTypes.COMBO_BOX:
            self.cfg[tab.key][setting.key] = setting.ui_widget.itemData(setting.ui_widget.currentIndex())

        elif setting.type == SettingTypes.INPUT:
            self.cfg[tab.key][setting.key] = setting.ui_widget.text()

        self.model.settings_event.demand()

        if do_update:
            self.model.update()