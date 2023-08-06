import gettext
import locale
import sys
from unittest import TestCase

from PySide import QtCore, QtGui

from maverig.models.model import Model, ProgramMode, Mode
from maverig.presenter.presenterManager import PresenterManager
from maverig.data import dataHandler, config
from maverig.data.config import ConfigKeys
from maverig.views.menuBarView import MenuBarView
from maverig.views.progressView import ProgressView
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.statusBarView import StatusBarView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.toolbarView import ToolbarView
from maverig.views.modePanelView import ModePanelView
from maverig.views.attributePanelView import AttributePanelView


try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestModePanelPresenter(TestCase):
    def setUp(self):
        self.model = Model()
        cfg = config.read_config()
        self.presenter_manager = PresenterManager(self.model, cfg)
        self.mode_panel_view = ModePanelView()

        # Install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        menu_bar_view = MenuBarView()
        property_panel_view = PropertyPanelView()
        tool_bar_view = ToolbarView()
        scenario_panel_view = ScenarioPanelView()
        status_bar_view = StatusBarView()
        progress_view = ProgressView()
        console_panel_view = ConsolePanelView()
        attribute_panel_view = AttributePanelView()

        self.presenter_manager.menu_bar_presenter.view = menu_bar_view
        self.presenter_manager.property_panel_presenter.view = property_panel_view
        self.presenter_manager.toolbar_presenter.view = tool_bar_view
        self.presenter_manager.scenario_panel_presenter.view = scenario_panel_view
        self.presenter_manager.status_bar_presenter.view = status_bar_view
        self.presenter_manager.progress_presenter.view = progress_view
        self.presenter_manager.console_panel_presenter.view = console_panel_view
        self.presenter_manager.attribute_panel_presenter.view = attribute_panel_view

        menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        tool_bar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        scenario_panel_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        progress_view.associated_presenter = self.presenter_manager.progress_presenter
        console_panel_view.associated_presenter = self.presenter_manager.console_panel_presenter
        attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter

        menu_bar_view.init_ui()
        property_panel_view.init_ui()
        tool_bar_view.init_ui()
        scenario_panel_view.init_ui()
        status_bar_view.init_ui()
        progress_view.init_ui()
        console_panel_view.init_ui()
        attribute_panel_view.init_ui()

        self.presenter_manager.mode_panel_presenter.view = self.mode_panel_view
        self.mode_panel_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        self.mode_panel_view.init_ui()
        self.mode_panel_presenter = self.presenter_manager.mode_panel_presenter

    def test_remove_selected_component_and_restore_default_components(self):
        """Removes a component and restores the default components. The list of hided components in the config
        gets cleared."""
        self.mode_panel_presenter.restore_default_components()
        self.mode_panel_presenter.selected_comp = "CSV.CHP"

        assert "CSV.CHP" in self.model.components

        self.mode_panel_presenter.remove_selected_component()

        assert not "CSV.CHP" in self.model.components

        self.mode_panel_presenter.restore_default_components()

        assert "CSV.CHP" in self.model.components

    def test_hide_selected_component(self):
        """Hides a component."""
        selected_comp = self.mode_panel_presenter.selected_comp = "PyPower.RefBus"
        invisible_components = self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS]
        if selected_comp in invisible_components:
            invisible_components.remove(selected_comp)
            self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS] = invisible_components
            config.write_config(self.mode_panel_presenter.cfg)

        assert not selected_comp in self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS]

        self.mode_panel_presenter.hide_selected_component()

        assert selected_comp in self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS]

        self.mode_panel_presenter.hide_selected_component()

        assert not selected_comp in self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS]

    def test_show_invisible_components(self):
        selected_comp = self.mode_panel_presenter.selected_comp = "PyPower.Branch"
        invisible_components = self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS]
        if selected_comp in invisible_components:
            invisible_components.remove(selected_comp)
            self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS] = invisible_components
        if self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.SHOW_INVISIBLE_COMPONENTS]:
            self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.SHOW_INVISIBLE_COMPONENTS] = False
        self.mode_panel_presenter.hide_selected_component()

        assert selected_comp in self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS]
        assert not self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.SHOW_INVISIBLE_COMPONENTS]

        self.mode_panel_presenter.show_invisible_components()

        assert self.mode_panel_presenter.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.SHOW_INVISIBLE_COMPONENTS]

        self.mode_panel_presenter.show_invisible_components()
        self.mode_panel_presenter.hide_selected_component()

    def test_selection_mode_btn_clicked(self):
        """Switches the mode between Selection Mode and Component Mode, if the Selection Mode Button is clicked"""
        self.model.mode = "component mode"
        self.mode_panel_presenter.selection_mode_btn_clicked()

        assert self.model.mode == "selection mode"

        self.mode_panel_presenter.selection_mode_btn_clicked()

        assert self.model.mode == "component mode"

    def test_hand_mode_btn_clicked(self):
        """Switches the mode between Hand Mode and Component Mode, if the Hand Mode Button is clicked"""
        self.model.mode = "component mode"
        self.mode_panel_presenter.hand_mode_btn_clicked()

        assert self.model.mode == "hand mode"

        self.mode_panel_presenter.hand_mode_btn_clicked()

        assert self.model.mode == "component mode"

    def test_comp_btn_created(self):
        """Adds created button to buttons dict."""
        assert not "PyPower.Bus" in self.mode_panel_presenter.buttons

        btn = self.mode_panel_view.create_button(dataHandler.get_icon('menubar/delete.png'), "blubb")
        self.mode_panel_presenter.comp_btn_created(btn, "PyPower.Bus")

        assert "PyPower.Bus" in self.mode_panel_presenter.buttons

    def test_comp_btn_clicked(self):
        """Switches the mode between Component Mode and Selection Mode, if one Component Button is clicked"""
        self.mode_panel_presenter.comp_btn_clicked(None, "PyPower.PQBus")

        assert self.model.mode == Mode.comp

        self.mode_panel_presenter.comp_btn_clicked(None, "PyPower.PQBus")
        self.mode_panel_presenter.comp_btn_clicked(None, "PyPower.PQBus")

        assert self.model.mode == Mode.selection


    def test_drag_started(self):
        """Switches the mode to component mode when a component is dragged."""
        self.model.comp = "CSV.House"

        assert self.model.mode == "selection mode" and self.model.comp == "CSV.House"

        self.mode_panel_presenter.drag_started(None, "PyPower.RefBus")

        assert self.model.mode == Mode.comp and self.model.comp == "PyPower.RefBus"

    def test_on_change_visibility_triggered(self):
        """Triggers the visibility of the component panel"""
        self.mode_panel_presenter.on_change_visibility_triggered()

        assert not self.mode_panel_view.isHidden()

        self.mode_panel_presenter.on_change_visibility_triggered()

        assert self.mode_panel_view.isHidden()

        self.mode_panel_presenter.on_change_visibility_triggered()

    def test_on_mode(self):
        """ react on model mode changes and update the view buttons accordingly """
        btn = self.model.comp = "CSV.House"
        self.mode_panel_presenter.on_mode()

        assert self.mode_panel_view.btn_selection_mode.isChecked()
        assert not self.mode_panel_view.btn_hand_mode.isChecked()
        assert self.mode_panel_view.btn_selection_mode.width() == 55
        assert self.mode_panel_view.btn_hand_mode.width() == 55
        assert not self.mode_panel_presenter.buttons[btn].isChecked()

        self.model.mode = "hand mode"
        self.mode_panel_presenter.on_mode()

        assert self.mode_panel_view.btn_hand_mode.isChecked()
        assert not self.mode_panel_view.btn_selection_mode.isChecked()
        assert self.mode_panel_view.btn_selection_mode.width() == 55
        assert self.mode_panel_view.btn_hand_mode.width() == 55
        assert not self.mode_panel_presenter.buttons[btn].isChecked()

        self.model.mode = "component mode"
        self.mode_panel_presenter.on_mode()

        assert not self.mode_panel_view.btn_hand_mode.isChecked()
        assert not self.mode_panel_view.btn_selection_mode.isChecked()
        assert self.mode_panel_view.btn_selection_mode.width() == 55
        assert self.mode_panel_view.btn_hand_mode.width() == 55
        assert self.mode_panel_presenter.buttons[btn].isChecked()

    def test_program_mode(self):
        """react on model program mode changes"""
        self.model.program_mode = ProgramMode.composition
        self.mode_panel_presenter.on_program_mode()

        if self.mode_panel_presenter.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_COMPONENT_PANEL_VISIBLE]:
            assert not self.mode_panel_view.isHidden()
        else:
            assert self.mode_panel_view.isHidden()

        self.model.program_mode = ProgramMode.simulation
        self.mode_panel_presenter.on_program_mode()

        assert self.mode_panel_view.isHidden()
