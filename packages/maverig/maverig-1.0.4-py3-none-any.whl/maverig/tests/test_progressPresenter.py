import gettext
import locale
from datetime import datetime
import sys
from unittest import TestCase
from maverig.models.model import ProgramMode

from PySide import QtCore, QtGui

from maverig.models.model import Model
from maverig.presenter.presenterManager import PresenterManager
from maverig.data import dataHandler, config
from maverig.views.attributePanelView import AttributePanelView
from maverig.views.modePanelView import ModePanelView
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.menuBarView import MenuBarView
from maverig.views.progressView import ProgressView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.settingsView import SettingsView
from maverig.views.statusBarView import StatusBarView
from maverig.views.toolbarView import ToolbarView

try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()

class TestProgressPresenter(TestCase):

    def setUp(self):
        self.model = Model()
        cfg = config.read_config()
        self.presenter_manager = PresenterManager(self.model, cfg)
        self.progress_view = ProgressView()

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
        scenario_panel_view = ScenarioPanelView()
        status_bar_view = StatusBarView()
        mode_panel_view = ModePanelView()
        self.progress_view = ProgressView()
        console_panel_view = ConsolePanelView()

        self.presenter_manager.settings_presenter.view = settings_view
        self.presenter_manager.attribute_panel_presenter.view = attribute_panel_view
        self.presenter_manager.menu_bar_presenter.view = menu_bar_view
        self.presenter_manager.property_panel_presenter.view = property_panel_view
        self.presenter_manager.toolbar_presenter.view = tool_bar_view
        self.presenter_manager.scenario_panel_presenter.view = scenario_panel_view
        self.presenter_manager.status_bar_presenter.view = status_bar_view
        self.presenter_manager.mode_panel_presenter.view = mode_panel_view
        self.presenter_manager.progress_presenter.view = self.progress_view
        self.presenter_manager.console_panel_presenter.view = console_panel_view

        attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter
        menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        tool_bar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        scenario_panel_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        mode_panel_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        self.progress_view.associated_presenter = self.presenter_manager.progress_presenter
        console_panel_view.associated_presenter = self.presenter_manager.console_panel_presenter
        settings_view.associated_presenter = self.presenter_manager.settings_presenter

        attribute_panel_view.init_ui()
        menu_bar_view.init_ui()
        property_panel_view.init_ui()
        tool_bar_view.init_ui()
        scenario_panel_view.init_ui()
        status_bar_view.init_ui()
        mode_panel_view.init_ui()
        self.progress_view.init_ui()
        console_panel_view.init_ui()

        self.timer = QtCore.QTimer()
        self.refresh = QtCore.QTimer()
        self.progress_presenter = self.presenter_manager.progress_presenter

    def test_on_slider_moved(self):
        """Sets simulation data index to current slider position. Keeps slider position valid if the mosaik simulation
        progress isn't as far as the position. The model performs lazy updates on the UI through the refresh_timer to
        prevent application from speed and graph animation issues."""
        self.model.sim_timestamps.append(datetime(2014, 10, 22, 4, 30, 00))
        self.model.sim_timestamps.append(datetime(2014, 10, 22, 4, 30, 00))
        self.model.sim_index = 0
        self.progress_presenter.on_slider_moved(0)

        assert self.model.sim_index == 0

        self.model.sim_index = 1
        self.progress_presenter.on_slider_moved(10)

        assert self.progress_view.slider.value() != 10
        assert self.progress_view.slider.value() == self.model.sim_index

    def test_on_change_visibility_triggered(self):
        """Toggles the visibility of the progress bar. Saves the visibility state in the config."""
        self.presenter_manager.progress_presenter.on_change_visibility_triggered()

        assert self.progress_view.isHidden()

        self.presenter_manager.progress_presenter.on_change_visibility_triggered()

        assert not self.progress_view.isHidden()

    def test_on_change_dateformat(self):
        """Toggles displaying of the date."""
        assert self.progress_presenter.date_format

        self.progress_presenter.on_change_dateformat()

        assert not self.progress_presenter.date_format

        self.date_format = False
        self.progress_presenter.on_change_dateformat()

    def test_on_screen_dateformat(self):
        """Reacts on changes of the date display. Displays the date as calendar date or as countdown."""
        self.progress_presenter.date_format = True
        self.model.sim_timestamps.append(datetime(2014, 10, 22, 4, 30, 00))
        self.model.update()
        self.progress_presenter.on_screen_dateformat()

        assert self.progress_view.end_date.text() == "2014-10-24"
        assert self.progress_view.end_time.text() == "23:59:59"
        assert self.progress_view.actual_date.text() == "2014-10-22"
        assert self.progress_view.actual_time.text() == "04:30:00"

        self.progress_presenter.date_format = False
        self.progress_presenter.on_screen_dateformat()

        assert self.progress_view.end_date.text() == "- 2 days"
        assert self.progress_view.end_time.text() == " 19:29:59"
        assert self.progress_view.actual_date.text() == "2 days"
        assert self.progress_view.actual_time.text() == " 4:30:00"

    def test_on_progress(self):
        """Applies the current progress to the progress bar."""
        self.model.sim_progress = 50
        self.progress_presenter.on_progress()

        assert self.progress_view.progress.value() == 50

        self.model.sim_progress = 100
        self.progress_presenter.on_progress()

        assert not self.model.output_event.demanded

    def test_on_sim(self):
        """Reacts on simulation data index changes. Updates the slider position and the date."""
        self.progress_view.slider.setMaximum(80)

        assert self.progress_view.slider.maximum() != self.model.sim_end_index

        self.progress_presenter.on_sim()

        assert self.progress_view.slider.maximum() == self.model.sim_end_index
        assert self.progress_view.slider.value() == self.model.sim_index

    def test_on_program_mode(self):
        """React on model program mode changes."""
        self.model.program_mode = ProgramMode.composition
        self.progress_presenter.on_program_mode()

        assert self.progress_view.isHidden()
        assert self.progress_view.progress.value() == 0
        assert self.progress_view.slider.value() == 0

        self.model.program_mode = ProgramMode.simulation
        self.progress_presenter.on_program_mode()

        assert self.progress_presenter.refresh_timer.isActive()
        assert not self.progress_view.isHidden()

        self.model.program_mode = ProgramMode.simulation_paused
        self.progress_presenter.on_program_mode()

        assert self.progress_presenter.refresh_timer.isActive()
        assert not self.progress_presenter.timer.isActive()

    def test_run_slider(self):
        """Starts the progress slider."""
        self.model.vid_speed = 8
        self.progress_presenter.run_slider()

        assert self.progress_presenter.timer.isActive()

    def test_stop_slider(self):
        """Stops the progress slider."""
        self.progress_presenter.stop_slider()

        assert not self.progress_presenter.timer.isActive()

    def test_run_iteration(self):
        """Updates the simulation data index which is responsible for moving the progress slider."""
        self.model.sim_timestamps.append(datetime(2014, 10, 22, 4, 30, 00))
        old = self.model.sim_index
        self.model.sim_timestamps.append(datetime(2014, 10, 22, 4, 30, 00))
        self.progress_presenter.run_iteration()

        assert old != self.model.sim_index