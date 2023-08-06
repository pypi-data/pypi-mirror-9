import sys
from unittest import TestCase

from PySide import QtCore, QtGui

from maverig.models.model import Model, Mode, ProgramMode
from maverig.presenter.presenterManager import PresenterManager
from maverig.views.attributePanelView import AttributePanelView
from maverig.views.modePanelView import ModePanelView
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.progressView import ProgressView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.statusBarView import StatusBarView
from maverig.views.menuBarView import MenuBarView
from maverig.views.toolbarView import ToolbarView
from maverig.data import config
from maverig.data.config import ConfigKeys

try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestStatusBarPresenter(TestCase):
    def setUp(self):

        # Load config
        cfg = config.read_config()

        self.model = Model()
        self.presenter_manager = PresenterManager(self.model, cfg)

        attribute_panel_view = AttributePanelView()
        menu_bar_view = MenuBarView()
        property_panel_view = PropertyPanelView()
        tool_bar_view = ToolbarView()
        scenario_panel_view = ScenarioPanelView()
        self.status_bar_view = StatusBarView()
        mode_panel_view = ModePanelView()
        progress_view = ProgressView()
        console_panel_view = ConsolePanelView()

        self.presenter_manager.attribute_panel_presenter.view = attribute_panel_view
        self.presenter_manager.menu_bar_presenter.view = menu_bar_view
        self.presenter_manager.property_panel_presenter.view = property_panel_view
        self.presenter_manager.toolbar_presenter.view = tool_bar_view
        self.presenter_manager.scenario_panel_presenter.view = scenario_panel_view
        self.presenter_manager.status_bar_presenter.view = self.status_bar_view
        self.presenter_manager.mode_panel_presenter.view = mode_panel_view
        self.presenter_manager.progress_presenter.view = progress_view
        self.presenter_manager.console_panel_presenter.view = console_panel_view

        attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter
        menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        tool_bar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        scenario_panel_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        self.status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        mode_panel_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        progress_view.associated_presenter = self.presenter_manager.progress_presenter
        console_panel_view.associated_presenter = self.presenter_manager.console_panel_presenter

        attribute_panel_view.init_ui()
        menu_bar_view.init_ui()
        property_panel_view.init_ui()
        tool_bar_view.init_ui()
        scenario_panel_view.init_ui()
        self.status_bar_view.init_ui()
        mode_panel_view.init_ui()
        progress_view.init_ui()
        console_panel_view.init_ui()

        self.status_bar_presenter = self.presenter_manager.status_bar_presenter

    def test_on_change_visibility_triggered(self):
        """Triggers the visibility of the status bar."""
        if self.status_bar_presenter.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE]:
            assert not self.status_bar_view.isHidden()
            self.status_bar_presenter.on_change_visibility_triggered()
            assert self.status_bar_view.isHidden()
            self.status_bar_presenter.on_change_visibility_triggered()
        else:
            assert self.status_bar_view.isHidden()
            self.status_bar_presenter.on_change_visibility_triggered()
            assert not self.status_bar_view.isHidden()
            self.status_bar_presenter.on_change_visibility_triggered()

    def test_on_mode(self):
        """Reacts on mode changes. Displays the chosen mode in the status bar."""
        self.model.mode = Mode.selection
        self.status_bar_presenter.on_mode()

        assert self.status_bar_view.status_message.text() == "selection mode"

        self.model.mode = Mode.hand
        self.status_bar_presenter.on_mode()

        assert self.status_bar_view.status_message.text() == "hand mode"

        self.model.mode = Mode.comp
        self.status_bar_presenter.on_mode()

        assert self.status_bar_view.status_message.text() == "component creation mode"

    def test_on_vid_speed_event(self):
        """Reacts on changes of the progress slider speed. Displays the current speed in the status bar."""
        self.model.program_mode = ProgramMode.simulation
        self.status_bar_presenter.on_vid_speed_event()

        assert self.status_bar_view.status_message.text() == "simulation mode: visualisation speed: 1x"

        self.model.program_mode = ProgramMode.simulation_paused
        self.status_bar_presenter.on_vid_speed_event()

        assert self.status_bar_view.status_message.text() == "simulation mode: visualisation speed: 1x: (paused)"

    def test_on_program_mode(self):
        """Reacts on program mode changes. The status bar is visible in every program mode if the user didn't hide
        it."""
        self.model.program_mode = ProgramMode.composition
        self.model.mode = Mode.selection
        self.status_bar_presenter.on_program_mode()

        assert self.status_bar_view.status_message.text() == "selection mode"
        assert self.status_bar_view.isHidden() != self.status_bar_presenter.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE]

        self.model.program_mode = ProgramMode.simulation
        self.status_bar_presenter.on_program_mode()

        assert self.status_bar_view.status_message.text() == "simulation mode: visualisation speed: 1x"
        assert self.status_bar_view.isHidden() != self.status_bar_presenter.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE]

        self.model.program_mode = ProgramMode.simulation_paused
        self.status_bar_presenter.on_program_mode()

        assert self.status_bar_view.status_message.text() == "simulation mode: visualisation speed: 1x: (paused)"
        assert self.status_bar_view.isHidden() != self.status_bar_presenter.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_STATUS_BAR_VISIBLE]

    def test_error(self):
        """Sets the given message in the status bar."""
        test_message = "Test"
        self.status_bar_presenter.error(test_message)

        assert self.status_bar_presenter.view.status_message.text() == test_message

    def test_info(self):
        """Sets the given message in the status bar."""
        test_message = "Test"
        self.status_bar_presenter.info(test_message)

        assert self.status_bar_presenter.view.status_message.text() == test_message

    def test_success(self):
        """Sets the given message in the status bar."""
        test_message = "Test"
        self.status_bar_presenter.success(test_message)

        assert self.status_bar_presenter.view.status_message.text() == test_message

    def test_reset(self):
        """Resets the state of the status bar."""
        test_message = "Nothing to report."
        self.status_bar_presenter.reset()

        assert self.status_bar_presenter.view.status_message.text() == test_message



