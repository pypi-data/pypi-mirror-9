import gettext
import locale
import sys
from unittest import TestCase

from PySide import QtCore, QtGui

from maverig.models.model import Model, Mode, ProgramMode
from maverig.presenter.presenterManager import PresenterManager
from maverig.data import dataHandler
from maverig.views.toolbarView import ToolbarView
from maverig.data import dataHandler, config

try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestToolBarPresenter(TestCase):
    def setUp(self):

        # Load config
        cfg = config.read_config()

        self.model = Model()
        presenter_manager = PresenterManager(self.model, cfg)
        self.toolbar_view = ToolbarView()

        # Install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        presenter_manager.toolbar_presenter.view = self.toolbar_view
        self.toolbar_view.associated_presenter = presenter_manager.toolbar_presenter

        self.toolbar_view.init_ui()
        self.toolbar_presenter = presenter_manager.toolbar_presenter

    def test_on_elements(self):
        """Reacts on changes of the elements count and toggles the state (checked/unchecked/enabled/disabled) of the
        depending actions."""
        self.toolbar_presenter.on_elements()

        assert len(self.model.elements) == 0
        assert not self.toolbar_view.action_auto_layout.isEnabled()
        assert not self.toolbar_view.action_zoom_fit.isEnabled()

        self.model.create_element('PyPower.PQBus', QtCore.QPointF(150.0, 200.0))
        self.model.force_dragging = True
        self.toolbar_presenter.on_elements()

        assert len(self.model.elements) > 0
        assert not self.toolbar_view.action_auto_layout.isEnabled()
        assert self.toolbar_view.action_zoom_fit.isEnabled()

    def test_on_selection(self):
        """Reacts on model changes of the current selection and toggles the state of the delete action."""
        self.toolbar_presenter.on_selection()

        assert not self.toolbar_presenter.view.action_delete.isEnabled()

        self.toolbar_presenter.model.mode = Mode.comp
        elem = self.model.create_element('PyPower.PQBus', QtCore.QPointF(150.0, 200.0))
        self.model.set_selected(elem, True)
        self.toolbar_presenter.on_selection()

        assert self.toolbar_presenter.view.action_delete.isEnabled()

    def test_on_drag(self):
        """Set the current mode"""
        self.toolbar_presenter.model.force_dragging = False
        self.toolbar_presenter.view.action_auto_layout.setEnabled(not self.toolbar_presenter.model.force_dragging)

        assert self.toolbar_presenter.view.action_auto_layout.isEnabled() == True

    def test_on_sim(self):
        """Reacts on changes of the simulation time and speed parameters and toggles the state
        (checked/unchecked/enabled/disabled) of the depending actions."""
        self.model.program_mode = ProgramMode.simulation
        self.model.sim_index = 1
        self.toolbar_presenter.on_sim()

        assert self.toolbar_view.action_run.isEnabled()

    def test_on_vid_speed(self):
        """Reacts on changes of the progress slider speed and toggles the state (checked/unchecked/enabled/disabled) of
        the depending actions."""
        self.model.program_mode = ProgramMode.simulation
        self.model.vid_speed_rel = 8
        self.toolbar_presenter.on_vid_speed()

        assert not self.toolbar_view.action_increase_speed.isEnabled()

        self.model.vid_speed_rel = 0.5
        self.toolbar_presenter.on_vid_speed()

        assert not self.toolbar_view.action_reduce_speed.isEnabled()

        self.model.vid_speed_rel = 5
        self.toolbar_presenter.on_vid_speed()

        assert self.toolbar_view.action_increase_speed.isEnabled()
        assert self.toolbar_view.action_reduce_speed.isEnabled()

    def test_on_program_mode(self):
        """Reacts on program mode changes and toggles the state (checked/unchecked/enabled/disabled) of the depending
        actions."""
        self.model.program_mode = ProgramMode.composition
        self.toolbar_presenter.on_program_mode()

        assert self.toolbar_view.action_open.isEnabled()
        assert not self.toolbar_view.action_back_to_start.isEnabled()
        assert not self.toolbar_view.action_reduce_speed.isEnabled()
        assert not self.toolbar_view.action_increase_speed.isEnabled()
        assert not self.toolbar_view.action_forward_to_end.isEnabled()
        assert not self.toolbar_view.action_stop.isEnabled()
        assert self.toolbar_view.action_run.isEnabled()

        self.model.program_mode = ProgramMode.simulation
        self.model.vid_speed_rel = 5
        self.model.sim_index = 1
        self.toolbar_presenter.on_program_mode()

        assert not self.toolbar_view.action_open.isEnabled()
        assert self.toolbar_view.action_back_to_start.isEnabled()
        assert self.toolbar_view.action_reduce_speed.isEnabled()
        assert self.toolbar_view.action_increase_speed.isEnabled()
        assert self.toolbar_view.action_forward_to_end.isEnabled()
        assert self.toolbar_view.action_stop.isEnabled()
        assert self.toolbar_view.action_run.isEnabled()

        self.model.program_mode = ProgramMode.simulation_paused
        self.toolbar_presenter.on_program_mode()

        assert self.toolbar_view.action_stop.isEnabled()
        assert self.toolbar_view.action_run.isEnabled()








