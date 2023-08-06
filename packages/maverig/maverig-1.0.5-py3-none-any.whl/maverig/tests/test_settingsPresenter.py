import gettext
import locale
import sys
from unittest import TestCase

from PySide import QtCore, QtGui

from maverig.models.model import Model
from maverig.presenter.presenterManager import PresenterManager
from maverig.views.attributePanelView import AttributePanelView
from maverig.views.modePanelView import ModePanelView
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.menuBarView import MenuBarView
from maverig.views.progressView import ProgressView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.settingsView import SettingsView
from maverig.data import dataHandler, config
from maverig.views.statusBarView import StatusBarView
from maverig.views.toolbarView import ToolbarView

try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestSettingsPresenter(TestCase):
    def setUp(self):

        # Load config
        self.cfg = config.read_config()

        model = Model()
        self.presenter_manager = PresenterManager(model, self.cfg)

        # Install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        settings_view = SettingsView()
        attribute_panel_view = AttributePanelView()
        menu_bar_view = MenuBarView()
        property_panel_view = PropertyPanelView()
        tool_bar_view = ToolbarView()
        self.scenario_panel_view = ScenarioPanelView()
        status_bar_view = StatusBarView()
        mode_panel_view = ModePanelView()
        progress_view = ProgressView()
        console_panel_view = ConsolePanelView()

        self.presenter_manager.settings_presenter.view = settings_view
        self.presenter_manager.attribute_panel_presenter.view = attribute_panel_view
        self.presenter_manager.menu_bar_presenter.view = menu_bar_view
        self.presenter_manager.property_panel_presenter.view = property_panel_view
        self.presenter_manager.toolbar_presenter.view = tool_bar_view
        self.presenter_manager.scenario_panel_presenter.view = self.scenario_panel_view
        self.presenter_manager.status_bar_presenter.view = status_bar_view
        self.presenter_manager.mode_panel_presenter.view = mode_panel_view
        self.presenter_manager.progress_presenter.view = progress_view
        self.presenter_manager.console_panel_presenter.view = console_panel_view

        attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter
        menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        tool_bar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        self.scenario_panel_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        mode_panel_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        progress_view.associated_presenter = self.presenter_manager.progress_presenter
        console_panel_view.associated_presenter = self.presenter_manager.console_panel_presenter
        settings_view.associated_presenter = self.presenter_manager.settings_presenter

        attribute_panel_view.init_ui()
        menu_bar_view.init_ui()
        property_panel_view.init_ui()
        tool_bar_view.init_ui()
        self.scenario_panel_view.init_ui()
        status_bar_view.init_ui()
        mode_panel_view.init_ui()
        progress_view.init_ui()
        console_panel_view.init_ui()

        # settings_view.show(self.cfg)
        self.settings_presenter = self.presenter_manager.settings_presenter

    def test_install_language(self):
        """Sets chosen language if it is changed by user. This is handled separately to prevent handling of unnecessary
        events in whole application if the language hasn't been changed."""
        if self.settings_presenter.model.language == "de_DE":
            language = "en_EN"
        elif self.settings_presenter.model.language == "en_EN":
            language = "de_DE"
        elif self.settings_presenter.model.language == "fr_FR":
            language = "de_DE"
        else:
            language = "de_DE"
        self.settings_presenter.install_language(True)

        assert self.settings_presenter.model.language != language

    def test_apply_setting(self):
        """Applies the given setting."""
        self.settings_presenter.cfg['simulation_settings']['is_day_night_vis_enabled'] = False

        config.write_config(self.settings_presenter.cfg)

        assert self.settings_presenter.cfg['simulation_settings']['is_day_night_vis_enabled'] == False

