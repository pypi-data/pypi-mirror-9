import sys
import gettext
import locale
from unittest import TestCase

from PySide import QtGui, QtCore

from maverig.presenter.presenterManager import PresenterManager
from maverig.models.model import Model, Mode
from maverig.views.attributePanelView import AttributePanelView
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.statusBarView import StatusBarView
from maverig.views.menuBarView import MenuBarView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.toolbarView import ToolbarView
from maverig.views.modePanelView import ModePanelView
from maverig.views.progressView import ProgressView
from maverig.data import dataHandler, config


try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestScenarioPanelPresenter(TestCase):
    def setUp(self):

        # Load config
        cfg = config.read_config()

        self.model = Model()
        self.presenter_manager = PresenterManager(self.model, cfg)

        # install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        attribute_panel_view = AttributePanelView()
        menu_bar_view = MenuBarView()
        property_panel_view = PropertyPanelView()
        tool_bar_view = ToolbarView()
        self.scenario_panel_view = ScenarioPanelView()
        status_bar_view = StatusBarView()
        mode_panel_view = ModePanelView()
        progress_view = ProgressView()
        console_panel_view = ConsolePanelView()

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

        attribute_panel_view.init_ui()
        menu_bar_view.init_ui()
        property_panel_view.init_ui()
        tool_bar_view.init_ui()
        self.scenario_panel_view.init_ui()
        status_bar_view.init_ui()
        mode_panel_view.init_ui()
        progress_view.init_ui()
        console_panel_view.init_ui()

        self.elem_pos = QtCore.QPointF(213, 232)
        self.elem_id = self.model.create_element('PyPower.PQBus', self.elem_pos)
        self.elem = self.model.elements[self.elem_id]
        self.model.update()

    def test_adjust_scene_rect(self):
        """Fits the size of the scene to the items_bounding_rect."""
        items_bounding_rect = self.scenario_panel_view.scene.itemsBoundingRect()
        # keep some margin to the edges
        items_bounding_rect.adjust(-15, -15, 15, 15)
        frame_rect = self.scenario_panel_view.mapToScene(self.scenario_panel_view.frameRect()).boundingRect()
        if self.presenter_manager.scenario_panel_presenter.start:
            frame_rect.adjust(1, 1, -1, -1)
            self.presenter_manager.scenario_panel_presenter.start = False
        scene_rect = frame_rect | items_bounding_rect
        self.scenario_panel_view.scene.setSceneRect(scene_rect)

        assert self.scenario_panel_view.scene.sceneRect() == frame_rect

    def test_element_at(self):
        """Returns element at mouse position."""
        element = self.presenter_manager.scenario_panel_presenter.element_at(self.elem_pos)

        assert element == None

    def test_group_presenters(self):
        """Returns a set of all group presenters."""
        group_presenter = self.presenter_manager.scenario_panel_presenter.group_presenters

        assert len(group_presenter) == 1

        self.elem_id = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200, 200))
        self.elem = self.model.elements[self.elem_id]
        self.model.update()
        group_presenter2 = self.presenter_manager.scenario_panel_presenter.group_presenters

        assert len(group_presenter2)

    def test_groups(self):
        """Returns a set of all groups."""
        group = self.presenter_manager.scenario_panel_presenter.groups

        assert len(group) == 1

        self.elem_id = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200, 200))
        self.elem = self.model.elements[self.elem_id]
        self.model.update()
        group2 = self.presenter_manager.scenario_panel_presenter.groups

        assert len(group2) == 2

    def test_mouse_clicked(self):
        """Create an element on clicking left mouse button
        switch between selection and component mode on clicking right mouse button."""
        self.model.selection_dragging = False
        self.model.mode = Mode.comp
        self.model.comp = "PyPower.RefBus"
        self.presenter_manager.scenario_panel_presenter.mouse_clicked(QtCore.QPointF(100, 100), QtCore.Qt.LeftButton)
        item = self.model.selection

        assert "PyPower.RefBus_1" in item
        self.model.deselect_all_elems()
        elem = self.model.create_element('PyPower.PQBus', QtCore.QPointF(150.0, 200.0))
        self.model.update()
        self.model.selection_dragging = False
        self.presenter_manager.scenario_panel_presenter.mouse_clicked(QtCore.QPointF(150.0, 200.0), QtCore.Qt.RightButton)

        assert self.presenter_manager.scenario_panel_presenter.element_at(QtCore.QPointF(150.0, 200.0))
        assert elem in self.model.selection

    def test_damped_mouse_pos(self):
        """Returns the damped mouse position if it is out of frame rect."""
        mouse_pos = QtCore.QPointF(-550, 243)
        self.presenter_manager.scenario_panel_presenter.vp_mouse.pos = mouse_pos
        damped_mouse = self.presenter_manager.scenario_panel_presenter.damped_mouse_pos(mouse_pos)

        assert damped_mouse != mouse_pos

        mouse_pos = QtCore.QPointF(0, 0)
        self.presenter_manager.scenario_panel_presenter.vp_mouse.pos = mouse_pos
        damped_mouse = self.presenter_manager.scenario_panel_presenter.damped_mouse_pos(mouse_pos)

        assert damped_mouse != mouse_pos

    def test_mouse_moved(self):
        """Set mouse position based on damped mouse position."""
        assert self.presenter_manager.scenario_panel_presenter.vp_mouse.pos == QtCore.QPointF(0, 0)

        mouse_pos = QtCore.QPointF(-200, 0)
        self.presenter_manager.scenario_panel_presenter.mouse_moved(mouse_pos, None)

        assert self.presenter_manager.scenario_panel_presenter.vp_mouse.pos == QtCore.QPointF(-10, 0)

    def test_mouse_released(self):
        """Draw second endpoint of line or transformer."""
        self.presenter_manager.scenario_panel_presenter.mouse_released(QtCore.QPointF(200, 200))

        assert len(self.model.history_undo) == 1

    def test_zoom(self):
        """Handles zooming functionality."""
        scale_distance = self.scenario_panel_view.matrix().scale(1.1, 1.1).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        self.presenter_manager.scenario_panel_presenter.zoom(True, None)
        scale_distance2 = self.scenario_panel_view.matrix().scale(1.1, 1.1).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        assert self.scenario_panel_view.isTransformed()
        assert scale_distance < scale_distance2

        scale_distance = self.scenario_panel_view.matrix().scale(1.1, 1.1).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        self.presenter_manager.scenario_panel_presenter.zoom(False, None)
        scale_distance2 = self.scenario_panel_view.matrix().scale(1.1, 1.1).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        assert self.scenario_panel_view.isTransformed()
        assert scale_distance > scale_distance2

    def test_zoom_fit(self):
        """Fits all elements into the view."""
        scale_distance = self.scenario_panel_view.matrix().scale(1.1, 1.1).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        self.presenter_manager.scenario_panel_presenter.zoom_fit()
        scale_distance2 = self.scenario_panel_view.matrix().scale(1.1, 1.1).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        assert self.scenario_panel_view.isTransformed()
        assert scale_distance2 > scale_distance

    def test_delete_selected_elements(self):
        """Deletes all selected elements."""
        self.model.set_selected(self.elem_id, True)
        self.model.update()

        assert self.elem_id in self.model.elements
        assert self.elem_id in self.model.selection

        self.presenter_manager.scenario_panel_presenter.delete_selected_elements()

        assert not self.elem_id in self.model.elements
        assert not self.elem_id in self.model.selection

    def test_copy_selected_elements(self):
        """Copy all selected elements."""
        self.model.set_selected(self.elem_id, True)
        self.model.update()
        self.presenter_manager.scenario_panel_presenter.copy_selected_elements()
        assert self.elem_id in self.model.clipboard_elements

    def test_cut_selected_elements(self):
        """Cut all selected elements."""
        self.model.set_selected(self.elem_id, True)
        self.model.update()
        self.presenter_manager.scenario_panel_presenter.cut_selected_elements()

        assert self.elem_id in self.model.clipboard_elements
        assert not self.elem_id in self.model.elements
        assert not self.elem_id in self.model.selection
        assert not self.scenario_panel_view.scene.itemAt(self.elem_pos)

    def test_paste_elements(self):
        """Paste and select inserted elements."""
        self.model.set_selected(self.elem_id, True)
        self.model.update()
        self.presenter_manager.scenario_panel_presenter.copy_selected_elements()

        assert len(self.model.history_undo) == 0

        self.presenter_manager.scenario_panel_presenter.paste_elements()
        new_position = self.elem_pos - QtCore.QPointF(4.000000, -4.000000)

        self.scenario_panel_view.scene.itemAt(new_position)

        assert len(self.model.selection) == 1
        assert len(self.model.history_undo) == 1

    def test_select_all_elements(self):
        """Selects all elements."""
        assert len(self.model.selection) == 0

        self.presenter_manager.scenario_panel_presenter.select_all_elements()

        assert len(self.model.selection) == 1

        self.model.selection.clear()

        assert len(self.model.selection) == 0

        self.elem_id = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200, 200))
        self.elem = self.model.elements[self.elem_id]
        self.model.update()
        self.presenter_manager.scenario_panel_presenter.select_all_elements()

        assert len(self.model.selection) == 2

    def test_select_all_active_elements(self):
        """Selects all elements depending on the current active mode."""
        assert len(self.model.selection) == 0

        self.elem_id = self.model.create_element('PyPower.RefBus', QtCore.QPointF(213, 232))
        self.elem = self.model.elements[self.elem_id]
        self.model.update()
        self.presenter_manager.scenario_panel_presenter.select_all_active_elements(self.elem_pos)

        assert len(self.model.selection) == 1

        self.elem_id = self.model.create_element('PyPower.RefBus', QtCore.QPointF(213, 232))
        self.elem = self.model.elements[self.elem_id]
        self.model.update()
        self.presenter_manager.scenario_panel_presenter.select_all_active_elements(self.elem_pos)

        assert len(self.model.selection) == 2

    def test_on_mode(self):
        """Reacts on model mode changes and updates the view, which component is allowed to be created and selected."""
        self.model.mode = Mode.hand
        self.model.update()

        assert self.scenario_panel_view.dragMode() == self.scenario_panel_view.ScrollHandDrag
        assert not self.scenario_panel_view.isInteractive()

        self.model.mode = Mode.selection
        self.model.update()

        assert self.scenario_panel_view.dragMode() == self.scenario_panel_view.RubberBandDrag
        assert self.scenario_panel_view.isInteractive()

        self.model.mode = Mode.comp
        self.model.update()

        assert self.scenario_panel_view.dragMode() == self.scenario_panel_view.NoDrag
        assert self.scenario_panel_view.isInteractive()

    def test_on_elements(self):
        """Updates the view items when number of model elements has changed."""
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(100, 100))

        assert not self.scenario_panel_view.scene.itemAt(QtCore.QPointF(100, 100))

        self.presenter_manager.scenario_panel_presenter.on_elements()

        assert self.scenario_panel_view.scene.itemAt(QtCore.QPointF(100, 100))

    def test_run_force_layout(self):
        """Run the force atlas algorithm."""
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(100, 100))

        assert not self.scenario_panel_view.scene.itemAt(QtCore.QPointF(100, 100))

        self.model.selection_dragging = False
        self.model.mode = Mode.comp
        self.model.comp = "PyPower.Branch"
        self.presenter_manager.scenario_panel_presenter.line_taken = True
        self.presenter_manager.scenario_panel_presenter.mouse_clicked(QtCore.QPointF(100, 100), QtCore.Qt.LeftButton)
        self.presenter_manager.scenario_panel_presenter.mouse_clicked(QtCore.QPointF(-110.0, 275.0), QtCore.Qt.LeftButton)

        self.presenter_manager.scenario_panel_presenter.mouse_released(QtCore.QPointF(-110.0, 275.0))
        self.presenter_manager.scenario_panel_presenter.run_force_layout()

        assert self.scenario_panel_view.scene.itemAt(QtCore.QPointF(100, 100))
        assert not self.scenario_panel_view.scene.itemAt(self.elem_pos)
        assert len(self.model.elements) == 3