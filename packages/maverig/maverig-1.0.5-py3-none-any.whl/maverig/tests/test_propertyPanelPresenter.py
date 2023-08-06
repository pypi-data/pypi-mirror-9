import gettext
import locale
import sys
from unittest import TestCase

from PySide import QtCore, QtGui

from maverig.models.model import Model, ProgramMode
from maverig.data import dataHandler, config
from maverig.data.config import ConfigKeys
from maverig.models.model import ElemPort
from maverig.presenter.presenterManager import PresenterManager
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


class TestPropertyPanelPresenter(TestCase):
    def setUp(self):
        self.model = Model()
        self.cfg = config.read_config()
        self.presenter_manager = PresenterManager(self.model, self.cfg)

        # Install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        self.widget_param_names = dict()

        settings_view = SettingsView()
        attribute_panel_view = AttributePanelView()
        menu_bar_view = MenuBarView()
        self.property_panel_view = PropertyPanelView()
        tool_bar_view = ToolbarView()
        scenario_panel_view = ScenarioPanelView()
        status_bar_view = StatusBarView()
        mode_panel_view = ModePanelView()
        progress_view = ProgressView()
        console_panel_view = ConsolePanelView()

        self.property_panel_presenter = self.presenter_manager.property_panel_presenter

        self.presenter_manager.settings_presenter.view = settings_view
        self.presenter_manager.attribute_panel_presenter.view = attribute_panel_view
        self.presenter_manager.menu_bar_presenter.view = menu_bar_view
        self.presenter_manager.property_panel_presenter.view = self.property_panel_view
        self.presenter_manager.toolbar_presenter.view = tool_bar_view
        self.presenter_manager.scenario_panel_presenter.view = scenario_panel_view
        self.presenter_manager.status_bar_presenter.view = status_bar_view
        self.presenter_manager.mode_panel_presenter.view = mode_panel_view
        self.presenter_manager.progress_presenter.view = progress_view
        self.presenter_manager.console_panel_presenter.view = console_panel_view

        attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter
        menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        self.property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        tool_bar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        scenario_panel_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        mode_panel_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        progress_view.associated_presenter = self.presenter_manager.progress_presenter
        console_panel_view.associated_presenter = self.presenter_manager.console_panel_presenter
        settings_view.associated_presenter = self.presenter_manager.settings_presenter

        attribute_panel_view.init_ui()
        menu_bar_view.init_ui()
        self.property_panel_view.init_ui()
        tool_bar_view.init_ui()
        scenario_panel_view.init_ui()
        status_bar_view.init_ui()
        mode_panel_view.init_ui()
        progress_view.init_ui()
        console_panel_view.init_ui()

    def test_on_change_visibility_triggered(self):
        """Test the hidden feature of the property panel."""
        assert self.property_panel_view.isHidden

        self.property_panel_presenter.on_change_visibility_triggered()

        assert not self.property_panel_view.isHidden()

        self.property_panel_presenter.on_change_visibility_triggered()

    def test_check_spinbox(self):
        """Check that the spinbox switch to the right value."""
        elem_id = self.model.create_element('PyPower.PQBus', QtCore.QPointF(300, 60))
        self.model.set_selected(elem_id, True)
        self.model.update()
        s_box = None

        for widget, param_name in self.property_panel_presenter.widget_param_names.items():  # search the right widget in die dict
            if param_name == 'base_kv':
                s_box = widget
        self.property_panel_presenter.check_spinbox(s_box, 0.33)

        assert self.model.get_param_value(elem_id,'base_kv') == 0.4

        self.property_panel_presenter.check_spinbox(s_box, 0.33)

        assert self.model.get_param_value(elem_id,'base_kv') == 0.23

    def test_value_changed(self):
        """Test if a wrong value für an element is set in the model."""
        elem_id = self.model.create_element('PyPower.Transformer', QtCore.QPointF(300, 60))
        self.model.set_param_value(elem_id, 'online', False)
        self.model.set_selected(elem_id, True)
        self.model.update()
        s_box = None

        for widget, param_name in self.property_panel_presenter.widget_param_names.items():  # search the right widget in die dict
            if param_name == 'online':
                s_box = widget

        self.property_panel_presenter.value_changed(s_box, False)

        assert self.property_panel_presenter.model.get_param_value(elem_id, 'online') == False

        for widget, param_name in self.property_panel_presenter.widget_param_names.items():  # search the right widget in die dict
            if param_name == 'ttype':
                s_box = widget

        self.property_panel_presenter.value_changed(s_box, 'TRAFO_31')

        assert self.property_panel_presenter.model.get_param_value(elem_id, 'ttype') == 'TRAFO_31'

        elem_id2 = self.model.create_element('CSV.House', QtCore.QPointF(250.0, 50.0))
        self.model.set_param_value(elem_id2, 'datafile', dataHandler.get_normpath('maverig/tests/data/household_1_2.small.csv' ))
        self.model.set_selected(elem_id, False)
        self.model.set_selected(elem_id2, True)
        self.model.update()

        for widget, param_name in self.property_panel_presenter.widget_param_names.items():  # search the right widget in die dict
            if param_name == 'datafile':
                s_box = widget

        self.property_panel_presenter.value_changed(s_box, dataHandler.get_normpath('maverig/tests/data/household_3_4.small.csv' ))

        assert self.property_panel_presenter.model.get_param_value(elem_id2, 'datafile') == dataHandler.get_normpath('maverig/tests/data/household_3_4.small.csv' )

    def test_on_selection(self):
        """Check that the right widgets are placed in the property panel when selecting an element."""
        elem_id = self.model.create_element('PyPower.Transformer', QtCore.QPointF(300, 60))
        self.model.set_selected(elem_id, True)
        self.model.update()
        self.property_panel_presenter.on_selection()

        assert self.model.get_param_value(elem_id, 'ttype') == 'TRAFO_31'  # default value of a transformer
        assert self.model.get_param_value(elem_id, 'online')  # default value of a transformer
        assert self.model.get_param_value(elem_id, 'tap') == 0  # default value of a transformer

    def test_on_param(self):
        """Check that the right widgets are placed and up to date when changing a value of an element."""
        elem_id = self.model.create_element('PyPower.Transformer', QtCore.QPointF(300, 60))
        self.model.set_param_value(elem_id, 'online', False)
        self.model.set_param_value(elem_id, 'tap', 1)
        self.model.set_selected(elem_id, True)
        self.model.update()

        # search the right widget in die dict
        for widget, param_name in self.property_panel_presenter.widget_param_names.items():
            if param_name == 'online':
                online = widget
                online.setChecked(True)
            if param_name == 'tap':
                transformer_tap = widget
                transformer_tap.setValue(-2)

        self.property_panel_presenter.on_param()
        self.model.update()

        assert self.model.get_param_value(elem_id, 'tap') == -2
        assert self.model.get_param_value(elem_id, 'online')

    def test_on_program_mode(self):
        """React on model program mode changes."""
        self.model.program_mode = ProgramMode.composition
        self.property_panel_presenter.on_program_mode()

        assert self.property_panel_presenter.view.isHidden() != self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_PROPERTY_PANEL_VISIBLE]

        self.model.program_mode = ProgramMode.simulation
        self.property_panel_presenter.on_program_mode()

        assert self.property_panel_presenter.view.isHidden()
