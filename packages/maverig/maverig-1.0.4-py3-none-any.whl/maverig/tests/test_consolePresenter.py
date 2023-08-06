import gettext
import locale
import sys
from unittest import TestCase

from PySide import QtCore, QtGui

from maverig.models.model import Model, ProgramMode
from maverig.presenter.presenterManager import PresenterManager
from maverig.data import dataHandler, config
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.menuBarView import MenuBarView
from maverig.views.attributePanelView import AttributePanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.statusBarView import StatusBarView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.toolbarView import ToolbarView
from maverig.views.modePanelView import ModePanelView
from maverig.views.progressView import ProgressView


try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestConsolePresenter(TestCase):
    def setUp(self):
        self.model = Model()
        cfg = config.read_config()
        self.presenter_manager = PresenterManager(self.model, cfg)
        self.console_view = ConsolePanelView()

        # Install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        attribute_panel_view = AttributePanelView()
        menu_bar_view = MenuBarView()
        property_panel_view = PropertyPanelView()
        tool_bar_view = ToolbarView()
        scenario_panel_view = ScenarioPanelView()
        status_bar_view = StatusBarView()
        mode_panel_view = ModePanelView()
        progress_view = ProgressView()


        self.presenter_manager.attribute_panel_presenter.view = attribute_panel_view
        self.presenter_manager.menu_bar_presenter.view = menu_bar_view
        self.presenter_manager.property_panel_presenter.view = property_panel_view
        self.presenter_manager.toolbar_presenter.view = tool_bar_view
        self.presenter_manager.scenario_panel_presenter.view = scenario_panel_view
        self.presenter_manager.status_bar_presenter.view = status_bar_view
        self.presenter_manager.mode_panel_presenter.view = mode_panel_view
        self.presenter_manager.progress_presenter.view = progress_view

        attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter
        menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        tool_bar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        scenario_panel_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        mode_panel_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        progress_view.associated_presenter = self.presenter_manager.progress_presenter


        attribute_panel_view.init_ui()
        menu_bar_view.init_ui()
        property_panel_view.init_ui()
        tool_bar_view.init_ui()
        scenario_panel_view.init_ui()
        status_bar_view.init_ui()
        mode_panel_view.init_ui()
        progress_view.init_ui()

        self.presenter_manager.console_panel_presenter.view = self.console_view
        self.console_view.associated_presenter = self.presenter_manager.console_panel_presenter
        self.console_view.init_ui()

    def test_on_change_visibility_triggered(self):
        """Triggers the visibility of the console panel."""
        self.presenter_manager.console_panel_presenter.on_change_visibility_triggered()

        assert self.console_view.isHidden() == False

        self.presenter_manager.console_panel_presenter.on_change_visibility_triggered()

        assert self.console_view.isHidden() == True

    def test_on_console_clear_triggered(self):
        """Clear console"""
        self.console_view.txt_edit_console.append("test")

        assert self.console_view.txt_edit_console.document().isEmpty() == False

        self.presenter_manager.console_panel_presenter.on_console_clear_triggered()

        assert self.console_view.txt_edit_console.document().isEmpty() == True

    def test_program_mode(self):
        """react on model program mode changes"""
        self.model.program_mode = ProgramMode.composition

        assert self.console_view.isHidden() == True

        self.model.program_mode = ProgramMode.simulation

        assert self.console_view.isHidden() == True

    def test_on_output(self):
        """Appends the given output to the console output."""
        test_message = "Testing"
        self.presenter_manager.console_panel_presenter.on_output(test_message)

        assert self.presenter_manager.console_panel_presenter.view.txt_edit_console.document().isEmpty() == False