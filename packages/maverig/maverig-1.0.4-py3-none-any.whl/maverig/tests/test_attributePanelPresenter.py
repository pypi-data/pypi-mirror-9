import sys
import gettext
import locale

from unittest import TestCase
from PySide import QtCore, QtGui
import PySide

from maverig.models.model import Model, ProgramMode
from maverig.presenter.presenterManager import PresenterManager
from maverig.views.attributePanelView import AttributePanelView
from maverig.data import config, dataHandler
from maverig.views.menuBarView import MenuBarView
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.statusBarView import StatusBarView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.toolbarView import ToolbarView
from maverig.views.modePanelView import ModePanelView
from maverig.views.progressView import ProgressView
from maverig.data.config import ConfigKeys

try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestAttributePanelPresenter(TestCase):
    def setUp(self):
        self.model = Model()
        self.cfg = config.read_config()
        self.presenter_manager = PresenterManager(self.model, self.cfg)
        self.attribute_panel_view = AttributePanelView()

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
        mode_panel_view = ModePanelView()
        progress_view = ProgressView()
        console_panel_view = ConsolePanelView()

        self.presenter_manager.menu_bar_presenter.view = menu_bar_view
        self.presenter_manager.property_panel_presenter.view = property_panel_view
        self.presenter_manager.toolbar_presenter.view = tool_bar_view
        self.presenter_manager.scenario_panel_presenter.view = scenario_panel_view
        self.presenter_manager.status_bar_presenter.view = status_bar_view
        self.presenter_manager.mode_panel_presenter.view = mode_panel_view
        self.presenter_manager.progress_presenter.view = progress_view
        self.presenter_manager.console_panel_presenter.view = console_panel_view

        menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        tool_bar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        scenario_panel_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        mode_panel_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        progress_view.associated_presenter = self.presenter_manager.progress_presenter
        console_panel_view.associated_presenter = self.presenter_manager.console_panel_presenter

        menu_bar_view.init_ui()
        property_panel_view.init_ui()
        tool_bar_view.init_ui()
        scenario_panel_view.init_ui()
        status_bar_view.init_ui()
        mode_panel_view.init_ui()
        progress_view.init_ui()
        console_panel_view.init_ui()

        self.presenter_manager.attribute_panel_presenter.view = self.attribute_panel_view
        self.attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter
        self.attribute_panel_view.init_ui()

    def test_on_change_visibility_triggered(self):
        """Toggles the visibility of the attribute panel. Saves the visibility state in the config."""
        self.presenter_manager.attribute_panel_presenter.on_change_visibility_triggered()

        assert self.attribute_panel_view.isHidden() == False

        self.presenter_manager.attribute_panel_presenter.on_change_visibility_triggered()

        assert self.attribute_panel_view.isHidden() == True

    def test_on_change_graph_visibility_triggered(self):
        """Toggles the visibility of the different graphs in the attribute panel."""
        self.elem_pos = QtCore.QPointF(213, 232)
        self.elem_id = self.model.create_element('CSV.House', self.elem_pos)
        self.presenter_manager.attribute_panel_presenter.cells["P"] = self.attribute_panel_view.create_attribute_cell \
            ("P", "Active Power", "W", 30, self.elem_id, [288.55], \
             [PySide.QtGui.QColor.fromHslF(0.550000, 0.749996, 0.269993, 1.000000)], True)
        attribute_graphs_visible = self.cfg[ConfigKeys.UI_STATE][ConfigKeys.ATTRIBUTE_GRAPHS_VISIBLE]
        if "P" in self.cfg[ConfigKeys.UI_STATE][ConfigKeys.ATTRIBUTE_GRAPHS_VISIBLE]:
            attribute_graphs_visible.remove("P")
            self.cfg[ConfigKeys.UI_STATE][ConfigKeys.ATTRIBUTE_GRAPHS_VISIBLE] = attribute_graphs_visible
        self.presenter_manager.attribute_panel_presenter.on_change_graph_visibility_triggered("P")

        assert "P" in self.cfg[ConfigKeys.UI_STATE][ConfigKeys.ATTRIBUTE_GRAPHS_VISIBLE]

    def test_on_selection(self):
        """Reacts on selection changes. Creates attribute cells for the attribute panel."""
        #elem_ids = {elem_id for elem_id in self.model.elements}
        self.model.program_mode = ProgramMode.simulation
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(300, 70))
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(200, 80))
        self.model.selection = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()
        self.presenter_manager.attribute_panel_presenter.on_selection()

        assert not self.presenter_manager.attribute_panel_presenter.cells

    def test_on_program_mode(self):
        """Reacts on program mode changes. In the composition program mode the attribute panel is hided while the panel
        is visible in the simulation program mode if the user didn't hide it."""
        self.model.program_mode = ProgramMode.composition
        self.presenter_manager.attribute_panel_presenter.on_program_mode()

        assert self.attribute_panel_view.isHidden()
        assert not self.presenter_manager.attribute_panel_presenter.cells

        self.model.program_mode = ProgramMode.simulation

        assert not self.attribute_panel_view.isHidden() == self.cfg[ConfigKeys.UI_STATE][
            ConfigKeys.IS_ATTRIBUTE_PANEL_VISIBLE]


