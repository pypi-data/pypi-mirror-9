import sys
import locale
import gettext
from unittest import TestCase

from PySide import QtCore, QtGui

from maverig.data import config
from maverig.presenter.group_presenter.iconGroupPresenter import IconGroupPresenter
from maverig.presenter.group_presenter.nodeGroupPresenter import NodeGroupPresenter
from maverig.presenter.presenterManager import PresenterManager
from maverig.models.model import Model, ElemPort, Mode
from maverig.views.attributePanelView import AttributePanelView
from maverig.views.menuBarView import MenuBarView
from maverig.views.propertyPanelView import PropertyPanelView
from maverig.views.scenarioPanelView import ScenarioPanelView
from maverig.views.statusBarView import StatusBarView
from maverig.views.toolbarView import ToolbarView
from maverig.views.modePanelView import ModePanelView
from maverig.views.progressView import ProgressView
from maverig.views.consolePanelView import ConsolePanelView
from maverig.views.groups.iconGroup import IconGroup
from maverig.views.groups.nodeGroup import NodeGroup
from maverig.views.positioning.vPoint import VPoint, Change
from maverig.views.positioning.section import section_manager
from maverig.data import dataHandler


try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    app = QtCore.QCoreApplication.instance()


class TestGroupPresenter(TestCase):
    def setUp(self):
        # Install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        self.graphics_view = QtGui.QGraphicsView()

        self.scene = QtGui.QGraphicsScene()
        self.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)

        self.graphics_view.setScene(self.scene)

        self.model = Model()
        cfg = config.read_config()
        self.presenter_manager = PresenterManager(self.model, cfg)

        attribute_panel_view = AttributePanelView()
        menu_bar_view = MenuBarView()
        property_panel_view = PropertyPanelView()
        scenario_view = ScenarioPanelView()
        status_bar_view = StatusBarView()
        toolbar_view = ToolbarView()
        console_view = ConsolePanelView()
        mode_view = ModePanelView()
        progress_view = ProgressView()

        self.presenter_manager.attribute_panel_presenter.view = attribute_panel_view
        self.presenter_manager.menu_bar_presenter.view = menu_bar_view
        self.presenter_manager.property_panel_presenter.view = property_panel_view
        self.presenter_manager.scenario_panel_presenter.view = scenario_view
        self.presenter_manager.status_bar_presenter.view = status_bar_view
        self.presenter_manager.toolbar_presenter.view = toolbar_view
        self.presenter_manager.console_panel_presenter.view = console_view
        self.presenter_manager.mode_panel_presenter.view = mode_view
        self.presenter_manager.progress_presenter.view = progress_view

        attribute_panel_view.associated_presenter = self.presenter_manager.attribute_panel_presenter
        menu_bar_view.associated_presenter = self.presenter_manager.menu_bar_presenter
        property_panel_view.associated_presenter = self.presenter_manager.property_panel_presenter
        scenario_view.associated_presenter = self.presenter_manager.scenario_panel_presenter
        status_bar_view.associated_presenter = self.presenter_manager.status_bar_presenter
        toolbar_view.associated_presenter = self.presenter_manager.toolbar_presenter
        console_view.associated_presenter = self.presenter_manager.console_panel_presenter
        mode_view.associated_presenter = self.presenter_manager.mode_panel_presenter
        progress_view.associated_presenter = self.presenter_manager.progress_presenter

        attribute_panel_view.init_ui()
        menu_bar_view.init_ui()
        property_panel_view.init_ui()
        scenario_view.init_ui()
        status_bar_view.init_ui()
        toolbar_view.init_ui()
        console_view.init_ui()
        mode_view.init_ui()
        progress_view.init_ui()

    def __init_icon_presenter(self):
        elem_id = self.model.create_element('CSV.PV', QtCore.QPointF(250.0, 200.0))
        elem_positions = {ep.port: self.model.get_pos(ep) for ep in self.model.elem_ports(elem_id)}
        view = IconGroup(elem_positions, dataHandler.get_component_icon('pv.svg'))
        group_presenter = IconGroupPresenter(self.presenter_manager, self.model, elem_id, None)

        group_presenter.view = view
        view.associated_presenter = group_presenter
        group_presenter.init_scene_mapping(self.scene)
        view.init_view(self.scene)

        return group_presenter

    def __init_node_item(self, x, y):
        elem_id = self.model.create_element('PyPower.PQBus', QtCore.QPointF(x, y))
        elem_positions = {ep.port: self.model.get_pos(ep) for ep in self.model.elem_ports(elem_id)}

        view = NodeGroup(elem_positions)
        group_presenter = NodeGroupPresenter(self.presenter_manager, self.model, elem_id, None)
        group_presenter.view = view
        view.associated_presenter = group_presenter
        group_presenter.init_scene_mapping(self.scene)
        view.init_view(self.scene)

        return view

    def __init_icon_item(self, x, y):
        elem_id = self.model.create_element('CSV.House', QtCore.QPointF(x, y))
        elem_positions = {ep.port: self.model.get_pos(ep) for ep in self.model.elem_ports(elem_id)}

        view = IconGroup(elem_positions, dataHandler.get_component_icon('house.svg'))
        group_presenter = IconGroupPresenter(self.presenter_manager, self.model, elem_id, None)
        group_presenter.view = view
        view.associated_presenter = group_presenter
        group_presenter.init_scene_mapping(self.scene)
        view.init_view(self.scene)

        return view

    def test_ep(self):
        """Returns the element port to a virtual point."""
        group_presenter = self.__init_icon_presenter()
        ep = group_presenter.ep(group_presenter.view.icon.vp_center)

        assert isinstance(ep, ElemPort)
        assert ep.elem_id == group_presenter.elem_id
        assert ep.port == '0'

    def test_vp(self):
        """Returns the virtual point to an element port."""
        group_presenter = self.__init_icon_presenter()
        test_port = ElemPort(group_presenter.elem_id, '0')
        vp = group_presenter.vp(test_port)

        assert isinstance(vp, VPoint)
        assert vp.pos == group_presenter.view.pos

    def test_raster_snap_v_points(self):
        """Returns a list of virtual points that may snap to the raster."""
        group_presenter = self.__init_icon_presenter()
        for vp in group_presenter.raster_snap_v_points:
            assert isinstance(vp, VPoint)

    def test_init_scene_mapping(self):
        """Adds view items to the scene, sets related elem_id as tooltip for easier handling of errors and triggers
        scene mapping."""
        group_presenter = self.__init_icon_presenter()
        scene = group_presenter.scene
        group_presenter.init_scene_mapping(scene)

        for port, v_point in group_presenter.mappings_port_vp.items():
            assert v_point.last_positions == [v_point.pos]

    def test_remove(self):
        """Removes this whole group. Unsubscribes model events."""
        group_presenter = self.__init_icon_presenter()
        group_presenter.remove()

        for item in group_presenter.view.items:
            assert not item

    def test_snap_zone(self):
        """Returns a list of nearby virtual points (of other groups) sorted by distance (from near to far)."""
        group_presenter = self.__init_icon_presenter()
        snap_points = group_presenter.snap_zone(group_presenter.view.icon.vp_center)

        assert len(snap_points) == 0

        node_group_1 = self.__init_node_item(250.0, 200.0)
        node_group_2 = self.__init_node_item(255.0, 205.0)
        node_group_3 = self.__init_node_item(300.0, 280.0)
        snap_points_with_items = group_presenter.snap_zone(group_presenter.view.icon.vp_center)

        for vp in snap_points_with_items:
            assert isinstance(vp, VPoint)
        assert len(snap_points_with_items) == 2
        assert node_group_1.node.vp_center in snap_points_with_items
        assert node_group_2.node.vp_center in snap_points_with_items
        assert not node_group_3.node.vp_center in snap_points_with_items
        assert snap_points_with_items[0] == node_group_1.node.vp_center
        assert snap_points_with_items[1] == node_group_2.node.vp_center

    def test_can_dock(self):
        """Returns if virtual point from_vp can dock with virtual point to_vp if docking is accepted and from_vp is
        not docked to another virtual point already. A virtual point (e.g. endpoint) can have one outgoing
        connection only but may have several ingoing connections (e.g. node)."""
        group_presenter = self.__init_icon_presenter()
        node_group = self.__init_node_item(250.0, 200.0)
        icon_group = self.__init_icon_item(245.0, 200.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        from_vp = group_presenter.vp(elem_port)
        can_dock_to_node = group_presenter.can_dock(from_vp, node_group.node.vp_center)
        can_dock_to_icon = group_presenter.can_dock(from_vp, icon_group.icon.vp_center)

        assert can_dock_to_node
        assert not can_dock_to_icon

    def test_to_dockables(self):
        """Returns a list of virtual points from to_vps to which the virtual point from_vp can dock-out."""
        group_presenter = self.__init_icon_presenter()
        node_group_1 = self.__init_node_item(255.0, 205.0)
        node_group_2 = self.__init_node_item(260.0, 210.0)
        node_group_3 = self.__init_node_item(300.0, 280.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        from_vp = group_presenter.vp(elem_port)
        snap_points = group_presenter.snap_zone(from_vp)
        to_dockables = group_presenter.to_dockables(from_vp, snap_points)

        assert len(to_dockables) == 2
        assert node_group_1.node.vp_center in to_dockables and node_group_2.node.vp_center in to_dockables
        assert not node_group_3.node.vp_center in to_dockables
        assert to_dockables[0] == node_group_1.node.vp_center
        assert to_dockables[1] == node_group_2.node.vp_center

    def test_from_dockables(self):
        """Returns a list of virtual points from from_vps to which the virtual point to_vp can dock-in."""
        group_presenter = self.__init_icon_presenter()
        node_group_1 = self.__init_node_item(255.0, 205.0)
        elem_port = ElemPort(group_presenter.elem_id, '0')
        vp = group_presenter.vp(elem_port)
        snap_points = group_presenter.snap_zone(vp)
        from_dockables = group_presenter.from_dockables(snap_points, node_group_1.node.vp_center)

        assert not from_dockables

        self.__init_icon_item(255.0, 205.0)
        elem_port = ElemPort(group_presenter.elem_id, '0')
        vp = group_presenter.vp(elem_port)
        snap_points = group_presenter.snap_zone(vp)
        from_dockables_with_icon = group_presenter.from_dockables(snap_points, node_group_1.node.vp_center)

        assert from_dockables_with_icon

    def test_connectables(self):
        """ virtual points of other_vps where vp can dock-in or -out """
        group_presenter = self.__init_icon_presenter()
        node_group_1 = self.__init_node_item(255.0, 205.0)
        node_group_2 = self.__init_node_item(260.0, 210.0)
        node_group_3 = self.__init_node_item(300.0, 280.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        snap_points = group_presenter.snap_zone(vp)
        connectables = group_presenter.connectables(snap_points, vp)

        assert len(connectables) == 2
        assert node_group_1.node.vp_center in connectables and node_group_2.node.vp_center in connectables
        assert not node_group_3.node.vp_center in connectables
        assert connectables[0] == node_group_1.node.vp_center
        assert connectables[1] == node_group_2.node.vp_center

    def test_new_connectables(self):
        """Returns a list of virtual points from other_vps to which the virtual point vp can dock-in or dock-out if
        they are not docked already."""
        group_presenter = self.__init_icon_presenter()
        node_group_1 = self.__init_node_item(255.0, 205.0)
        node_group_2 = self.__init_node_item(260.0, 210.0)
        node_group_3 = self.__init_node_item(300.0, 280.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        snap_points = group_presenter.snap_zone(vp)
        new_connectables = group_presenter.new_connectables(snap_points, vp)

        assert len(new_connectables) == 2
        assert node_group_1.node.vp_center in new_connectables
        assert node_group_2.node.vp_center in new_connectables
        assert not node_group_3.node.vp_center in new_connectables
        assert new_connectables[0] == node_group_1.node.vp_center
        assert new_connectables[1] == node_group_2.node.vp_center

    def test_non_connectable(self):
        """Returns a list of virtual points from other_vps to which the virtual point vp can't dock."""
        group_presenter = self.__init_icon_presenter()
        self.__init_node_item(260.0, 210.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        snap_points = group_presenter.snap_zone(vp)
        has_non_connectables = group_presenter.non_connectable(snap_points, vp)

        assert not has_non_connectables

        self.__init_icon_item(255.0, 205.0)
        snap_points = group_presenter.snap_zone(vp)
        has_non_connectables_with_icon = group_presenter.non_connectable(snap_points, vp)

        assert has_non_connectables_with_icon

    def test_dock(self):
        """Docks virtual points and applies docking in model."""
        group_presenter = self.__init_icon_presenter()
        node_group = self.__init_node_item(250.0, 200.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        group_presenter.dock(vp, node_group.node.vp_center)

        assert vp.follows(node_group.node.vp_center)

    def test_undock(self):
        """Undocks virtual points and applies undocking in model."""
        group_presenter = self.__init_icon_presenter()
        node_group = self.__init_node_item(250.0, 200.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        group_presenter.dock(vp, node_group.node.vp_center)
        group_presenter.undock(vp, node_group.node.vp_center)

        assert not vp.follows(node_group.node.vp_center)

    def test_check_snap_permission(self):
        """Checks whether the view has permission to snap. Optionally validates snap restrictions."""
        group_presenter = self.__init_icon_presenter()
        deny_snap_pasted_elem = group_presenter.check_snap_permission(False)

        assert deny_snap_pasted_elem

        group_presenter.deny_snap_pasted_elem = True
        deny_snap_pasted_elem = group_presenter.check_snap_permission(True)

        assert not deny_snap_pasted_elem

    def test_on_position_changed(self):
        """Applies docking/undocking of the view within snap zone. Sets v_point position in model."""
        group_presenter = self.__init_icon_presenter()
        node_group = self.__init_node_item(250.0, 200.0)
        elem_port = ElemPort(group_presenter.elem_id, '0')
        vp = group_presenter.vp(elem_port)
        group_presenter.dock(vp, node_group.node.vp_center)

        assert vp.follows(node_group.node.vp_center)

        group_presenter.on_position_changed(node_group.node.vp_center, QtCore.QPointF(1.0, 1.0), Change.moved,
                                            section_manager.presenter_section)

        assert vp.follows(node_group.node.vp_center)

        group_presenter.on_position_changed(vp, QtCore.QPointF(1.0, 1.0), Change.snapped,
                                            section_manager.presenter_section)

        assert vp.follows(node_group.node.vp_center)

        vp.pos += QtCore.QPointF(1.0, 1.0)
        group_presenter.on_position_changed(vp, QtCore.QPointF(1.0, 1.0), Change.moved,
                                            section_manager.presenter_section)

        assert not vp.follows(node_group.node.vp_center)

    def test_validation(self):
        """Updates the views validity."""
        group_presenter = self.__init_icon_presenter()
        self.__init_node_item(55.0, 330.0)
        self.__init_icon_item(275.0, 220.0)
        ep = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(ep)
        snap_points = group_presenter.snap_zone(vp)
        has_non_connectables = group_presenter.validation(vp, snap_points)

        assert has_non_connectables == 'invalid'

        node_group = self.__init_node_item(495.0, 165.0)
        ep = group_presenter.ep(node_group.node.vp_center)
        vp = group_presenter.vp(ep)
        snap_points = group_presenter.snap_zone(vp)
        line_too_short = group_presenter.validation(vp, snap_points)

        assert line_too_short == 'line_too_short'

    def test_snap_dock(self):
        """Snaps the view to the raster."""
        group_presenter = self.__init_icon_presenter()
        node_group = self.__init_node_item(250.0, 200.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        group_presenter.snap_dock()

        assert vp.follows(node_group.node.vp_center)
        assert node_group.node.vp_center.follows(vp)

    def test_raster_snap(self):
        """Snaps the view to the raster if raster mode is enabled."""
        group_presenter = self.__init_icon_presenter()
        self.__init_node_item(234.0, 199.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        group_presenter.model.raster_snap_mode = True
        group_presenter.deny_snap_pasted_elem = False
        group_presenter.raster_snap()

        assert vp.pos == QtCore.QPointF(275.0, 220.0)

    def test_avoid_invalid_positions(self):
        """Avoids invalid positions by moving the view back to last valid positions."""
        group_presenter = self.__init_icon_presenter()
        self.__init_node_item(55.0, 330.0)
        ep = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(ep)
        snap_points = group_presenter.snap_zone(vp)
        moved = group_presenter.avoid_invalid_positions()

        assert moved
        assert vp.last_positions
        assert group_presenter.validation(vp, snap_points) == 'line_too_short'

        self.__init_icon_item(275.0, 220.0)
        group_presenter.snap_zone(vp)
        moved = group_presenter.avoid_invalid_positions()

        assert not moved

    def test_on_mouse_released(self):
        """Applies raster snapping to the view if view is released by the mouse."""
        group_presenter = self.__init_icon_presenter()
        group_presenter.position_has_changed = True
        node_group = self.__init_node_item(250.0, 200.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        group_presenter.on_mouse_released(None)

        assert vp.follows(node_group.node.vp_center)
        assert node_group.node.vp_center.follows(vp)

    def test_on_elements(self):
        """Reacts on changes on elements count and removes himself if view isn't present anymore."""
        group_presenter = self.__init_icon_presenter()
        len_before_remove = len(self.model.elements_event)
        self.model.elements.pop(group_presenter.elem_id)
        group_presenter.on_elements()
        len_after_remove = len(self.model.elements_event)

        assert len_before_remove - len_after_remove == 1

    def test_on_positions(self):
        """Reacts on position changes."""
        group_presenter = self.__init_icon_presenter()
        elem_port = ElemPort(group_presenter.elem_id, '0')
        vp = group_presenter.vp(elem_port)
        self.model.set_pos(elem_port, QtCore.QPointF(240.0, 240.0))

        assert vp.pos.x() == 250.0
        assert vp.pos.y() == 200.0

        group_presenter.on_positions()

        assert vp.pos.x() == 240.0
        assert vp.pos.y() == 240.0

    def test_on_drag(self):
        """Reacts on drag and drop."""
        group_presenter = self.__init_icon_presenter()
        self.__init_icon_item(234.0, 199.0)
        ep = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(ep)
        group_presenter.model.selection_dragging = False
        group_presenter.model.force_dragging = False
        group_presenter.model.raster_snap_mode = True
        group_presenter.position_has_changed = False
        group_presenter.deny_snap_pasted_elem = True
        group_presenter.on_drag()

        assert vp.pos == QtCore.QPointF(250.0, 200.0)

    def test_on_selection(self):
        """Reacts on selection changes. Updates the views z-mode and visibility state."""
        group_presenter = self.__init_icon_presenter()
        self.model.selection.append(group_presenter.elem_id)
        group_presenter.on_selection()

        assert group_presenter.view.selected

        self.model.selection.remove(group_presenter.elem_id)
        group_presenter.on_selection()

        assert not group_presenter.view.selected

    def test_on_dockings(self):
        """Reacts on view docking."""
        group_presenter = self.__init_icon_presenter()
        node_group = self.__init_node_item(250.0, 200.0)
        elem_port = ElemPort(group_presenter.elem_id, '1')
        vp = group_presenter.vp(elem_port)
        self.model.dock(elem_port, node_group.associated_presenter.ep(node_group.node.vp_center))

        assert not vp.follows(node_group.node.vp_center)

        group_presenter.on_dockings()

        assert vp.follows(node_group.node.vp_center)

    def test_on_mode(self):
        """Reacts on mode changes. Updates the state of the view."""
        group_presenter = self.__init_icon_presenter()
        group_presenter.model.mode = Mode.sim
        group_presenter.on_mode()

        assert group_presenter.view.enabled

        group_presenter.model.mode = Mode.comp
        group_presenter.on_mode()

        assert group_presenter.view.enabled == group_presenter.model.is_selectable(group_presenter.elem_id)

    def test_on_param(self):
        """Reacts on parameter changes."""
        group_presenter = self.__init_icon_presenter()
        group_presenter.view.icon.icon_path = dataHandler.get_component_icon('chp.svg')
        elem = group_presenter.model.elements[group_presenter.elem_id]

        assert not group_presenter.view.icon.icon_path == dataHandler.get_component_icon(elem['icon'])

        group_presenter.on_param()

        assert group_presenter.view.icon.icon_path == dataHandler.get_component_icon(elem['icon'])

    def test_change_ev_icon(self):
        """Changes the icon of an electric vehicle depending on state of charge and plugged-in state."""
        group_presenter = self.__init_icon_presenter()
        group_presenter.elem_id = self.model.create_element('CSV.EV', QtCore.QPointF(250.0, 55.0))
        elem_positions = {ep.port: self.model.get_pos(ep) for ep in self.model.elem_ports(group_presenter.elem_id)}
        view = IconGroup(elem_positions, dataHandler.get_component_icon('ev+battery.svg'))
        group_presenter = IconGroupPresenter(self.presenter_manager, self.model, group_presenter.elem_id, None)
        group_presenter.view = view
        view.associated_presenter = group_presenter
        group_presenter.init_scene_mapping(self.scene)
        view.init_view(self.scene)
        group_presenter.change_ev_icon(1)

        assert view.icon.icon_path == dataHandler.get_component_icon('ev/ev_consumer.svg')

        group_presenter.change_ev_icon(-1)

        assert view.icon.icon_path == dataHandler.get_component_icon('ev/ev_producer.svg')

        group_presenter.change_ev_icon(0)

        assert view.icon.icon_path == dataHandler.get_component_icon('ev+battery.svg')
