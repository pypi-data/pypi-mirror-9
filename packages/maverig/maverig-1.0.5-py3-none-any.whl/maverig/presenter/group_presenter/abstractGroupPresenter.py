from operator import itemgetter

from PySide import QtCore, QtGui
from PySide.QtCore import Qt
import numpy as np

import maverig.utils.colorTools as ct
from maverig.data import config, dataHandler
from maverig.data.config import ConfigKeys
from maverig.data.settings.heatValueEffect import HeatValueEffectKeys
from maverig.presenter.abstractPresenter import AbstractPresenter
from maverig.models.model import ElemPort, Mode, ProgramMode
from maverig.views.items.line import Line
from maverig.views.positioning.section import section_manager
from maverig.views.positioning.vPoint import Change


scene_mapping = dict()  # dict from scene to mapping between elem_port and v_point


class AbstractGroupPresenter(AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for all groups."""

    def __init__(self, presenter_manager, model, elem_id, cfg):
        """Initializes the abstract group presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super().__init__(presenter_manager, model, cfg)

        self.scene = None
        self.elem_id = elem_id

        # snap_radius must provide enough distance to non_connectables (greater than sqrt(2)*RASTER_SIZE/2)
        self.snap_radius = 0.75 * config.RASTER_SIZE

        self.direct_snap_radius = 15
        self.selected = None

        self.is_just_created = True

        # pasted elements can be moved freely without raster snapping until successful validation
        self.deny_snap_pasted_elem = False

        self.position_has_changed = False
        section_manager.presenter_section.exit_event += self.on_exit_presenter_section

        # react on model events with own methods
        self.model.elements_event += self.on_elements
        self.model.positions_event += self.on_positions
        self.model.selection_event += self.on_selection
        self.model.dockings_event += self.on_dockings
        self.model.mode_event += self.on_mode
        self.model.drag_event += self.on_drag
        self.model.param_event += self.on_param
        self.model.attrs_event += self.on_attrs

    @property
    def mappings_port_vp(self):
        """Maps the port and the v_point."""
        pass

    def ep(self, v_point):
        """Returns the element port belonging to a virtual point."""
        return scene_mapping[self.scene].get(v_point)

    def vp(self, elem_port):
        """Returns the virtual point belonging to an element port."""
        return scene_mapping[self.scene].get(elem_port)

    @property
    def raster_snap_v_points(self):
        """Returns a list of virtual points that may snap to the raster."""
        return list(self.mappings_port_vp.values())

    def init_scene_mapping(self, scene):
        """Adds view items to the scene, sets related elem_id as tooltip for easier handling of errors and triggers
        scene mapping."""
        for item in self.view.items:
            item.graphics_item.setToolTip(self.elem_id)
        self.scene = scene
        scene_mapping.setdefault(scene, dict())

        # add internal {port-->v_point}-mapping to global mapping {(elem_id, port)<-->v_point} based on scene
        for port, v_point in self.mappings_port_vp.items():
            v_point.last_positions = [v_point.pos]
            elem_port = ElemPort(self.elem_id, port)
            scene_mapping[scene][elem_port] = v_point
            scene_mapping[scene][v_point] = elem_port

    def remove(self):
        """Removes this whole group. Unsubscribes model events."""
        self.model.elements_event -= self.on_elements
        self.model.positions_event -= self.on_positions
        self.model.selection_event -= self.on_selection
        self.model.dockings_event -= self.on_dockings
        self.model.mode_event -= self.on_mode
        self.model.drag_event -= self.on_drag
        self.model.param_event -= self.on_param
        self.model.attrs_event -= self.on_attrs
        section_manager.presenter_section.exit_event -= self.on_exit_presenter_section

        for port, vp in self.mappings_port_vp.items():
            ep = ElemPort(self.elem_id, port)
            del scene_mapping[self.scene][ep]
            del scene_mapping[self.scene][vp]

        self.view.remove()

    def snap_zone(self, v_point, pos=None):
        """Returns a list of nearby virtual points (of other groups) sorted by distance (from near to far)."""
        scene = self.view.items[0].graphics_item.scene()

        if pos is None:
            pos = v_point.pos

        rect = QtCore.QRectF()
        rect.setSize(QtCore.QSizeF(self.snap_radius * 2, self.snap_radius * 2))
        rect.moveCenter(pos)

        near_vp_distances = []

        near_groups = [graphics_item.related_item.parent_group for graphics_item in scene.items(rect)
                       if hasattr(graphics_item, 'related_item')
                       and graphics_item.related_item.parent_group != v_point.parent_item.parent_group]

        near_v_points = [near_item.vp_center for near_group in near_groups for near_item in near_group.items
                         if not isinstance(near_item, Line)]

        for near_vp in near_v_points:
            distance = QtCore.QLineF(pos, near_vp.pos).length()
            if distance <= self.snap_radius:
                near_vp_distances.append((near_vp, distance))

        near_vp_distances.sort(key=itemgetter(1))  # sort by distance (second tuple index)

        return [vp[0] for vp in near_vp_distances]

    def can_dock(self, from_vp, to_vp):
        """Returns if virtual point from_vp can dock with virtual point to_vp if docking is accepted and from_vp is
        not docked to another virtual point already. A virtual point (e.g. endpoint) can have one outgoing
        connection only but may have several ingoing connections (e.g. node)."""
        from_ep = self.ep(from_vp)
        to_ep = self.ep(to_vp)
        has_no_other_dockings = from_vp.extern_followers in [[to_vp], []]

        return from_ep and to_ep and self.model.can_dock(from_ep, to_ep) and has_no_other_dockings

    def to_dockables(self, from_vp, to_vps):
        """Returns a list of virtual points from to_vps to which the virtual point from_vp can dock-out."""
        return [to_vp for to_vp in to_vps if self.can_dock(from_vp, to_vp)]

    def from_dockables(self, from_vps, to_vp):
        """Returns a list of virtual points from from_vps to which the virtual point to_vp can dock-in."""
        return [from_vp for from_vp in from_vps if self.can_dock(from_vp, to_vp)]

    def connectables(self, other_vps, vp):
        """Returns a list of virtual points from other_vps to which the virtual point vp can dock-in or dock-out."""
        return [other_vp for other_vp in other_vps if (self.can_dock(vp, other_vp) or self.can_dock(other_vp, vp))]

    def new_connectables(self, other_vps, vp):
        """Returns a list of virtual points from other_vps to which the virtual point vp can dock-in or dock-out if
        they are not docked already."""
        return [other_vp for other_vp in self.connectables(other_vps, vp) if not other_vp.follows(vp)]

    def non_connectable(self, other_vps, vp):
        """Returns a list of virtual points from other_vps to which the virtual point vp can't dock."""
        from_ep = self.ep(vp)
        from_ep2 = ElemPort(from_ep.elem_id, "0" if from_ep.port == "1" else "1")
        drawing_mode = lambda ep: self.model.get_component(ep.elem_id)['drawing_mode']
        relevant_branches = []

        for other_vp in other_vps:
            # case: one vp in general is not allowed to dock to another one
            if not self.can_dock(vp, other_vp) and not self.can_dock(other_vp, vp):
                vps1 = [vp] + vp.extern_followers
                vps2 = [other_vp] + other_vp.extern_followers
                if not any([self.can_dock(vp1, vp2) or self.can_dock(vp2, vp1)
                            for vp1 in vps1 for vp2 in vps2]):
                    return [other_vp]

            # case: one branch is normally allowed to dock to node B / refbus, but should not,
            # because the connection node A - node B already exists.
            if 'node' in drawing_mode(self.ep(other_vp)) or 'refbus' in drawing_mode(self.ep(other_vp)):

                # branch is and should not dock to node B, so the positions of branch eps are saved.
                first_docked_node_from_ep_pos = self.vp(from_ep).pos
                second_docked_node_from_ep_pos = self.vp(from_ep2).pos

                # save branches, which are already docked to interesting nodes
                for other_branches in self.model.dockings_in(self.ep(other_vp)):
                    if 'line' in drawing_mode(other_branches) and other_branches.elem_id != from_ep.elem_id:
                        relevant_branches.append(other_branches)

                for other_ep in relevant_branches:
                    other_ep2 = ElemPort(other_ep.elem_id, "0" if other_ep.port == "1" else "1")

                    # first ep of the branch is near an ep of the other branch.
                    near_node1 = QtCore.QLineF(first_docked_node_from_ep_pos, self.vp(other_ep).pos).length() \
                                 < self.snap_radius or QtCore.QLineF(first_docked_node_from_ep_pos, \
                                                                     self.vp(other_ep2).pos).length() < self.snap_radius

                    # second ep of the branch is near an ep of the other branch.
                    near_node2 = QtCore.QLineF(second_docked_node_from_ep_pos, self.vp(other_ep).pos).length() \
                                 < self.snap_radius or QtCore.QLineF(second_docked_node_from_ep_pos, \
                                                                     self.vp(other_ep2).pos).length() < self.snap_radius

                    # eps of branch are not too close, because they should not overlay each other.
                    # first_pos == second_pos allowed, so branch can be initialised on a node
                    point_overlay = QtCore.QLineF(first_docked_node_from_ep_pos, \
                                                  second_docked_node_from_ep_pos).length() < self.snap_radius and \
                                    first_docked_node_from_ep_pos == second_docked_node_from_ep_pos

                    if (near_node1 and near_node2) and not point_overlay:
                        return [self.vp(other_ep)]

        return []

    def dock(self, from_vp, to_vp):
        """Docks virtual points and applies docking in model."""
        self.model.dock(self.ep(from_vp), self.ep(to_vp))  # e.g. dock endpoint to node

        from_vp.follow(to_vp)
        # adjust if the whole line is moved --> endpoints are calculated
        to_vp.follow(from_vp, {Change.calculated, Change.raster_snapped, Change.avoid_invalid})

    def undock(self, from_vp, to_vp):
        """Undocks virtual points and applies undocking in model."""
        self.model.undock(self.ep(from_vp), self.ep(to_vp))
        from_vp.unfix(to_vp)

    def check_snap_permission(self, do_validate=False):
        """Checks whether the view has permission to snap. Optionally validates snap restrictions."""
        if self.deny_snap_pasted_elem and do_validate:
            validations = [self.validation(vp) for vp in self.raster_snap_v_points]
            valid = not set(validations) & {'invalid', 'line_too_short'}
            # Release snap restrictions if pasted element is valid
            if valid:
                self.deny_snap_pasted_elem = False
        return not self.deny_snap_pasted_elem

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_position_changed(self, vp, delta, change, section):
        """Applies docking/undocking of the view within snap zone. Sets v_point position in model."""
        if section != section_manager.presenter_section or not self.ep(vp):
            return

        self.position_has_changed = True
        ep = self.ep(vp)
        self.model.set_pos(ep, vp.pos)

        if change == Change.raster_snapped:
            self.model.positions_event.demand()
            self.model.update()

        if change == Change.moved:
            # temporary undock from all outgoing dockings with different positions
            for to_ep in self.model.dockings_out(ep):
                to_vp = self.vp(to_ep)
                if vp.pos != to_vp.pos:
                    self.undock(vp, to_vp)

            # snap with near connectable in smaller direct_snap_radius
            if self.model.selection == [self.elem_id]:
                snap_zone = self.snap_zone(vp)

                for other_vp in self.new_connectables(snap_zone, vp)[:1]:
                    if QtCore.QLineF(vp.pos, other_vp.pos).length() < self.direct_snap_radius:
                        vp.set_pos(other_vp.pos, Change.snapped)

        # inform the user about valid and invalid docking in the status bar.
        vp.last_positions.append(vp.pos)

    def on_exit_presenter_section(self, section):
        """Informs the user about docking validity via status bar messages."""
        if self.position_has_changed and self.model.selection == [self.elem_id] and not self.model.force_dragging:
            validations = [self.validation(vp) for vp in self.raster_snap_v_points]
            if 'invalid' in validations:
                self.presenter_manager.status_bar_presenter.error(config.DOCKING_INVALID())
            elif 'line_too_short' in validations:
                self.presenter_manager.status_bar_presenter.error(config.LINE_TOO_SHORT())
            elif 'valid' in validations:
                self.presenter_manager.status_bar_presenter.success(config.DOCKING_VALID())
            else:
                self.presenter_manager.status_bar_presenter.info(config.DOCKING_NO_ITEMS())

    def validation(self, vp, snap_zone=None):
        """Updates the views validity."""
        if snap_zone is None:
            snap_zone = self.snap_zone(vp)

        # check whether line is to short
        rastered_positions = {config.raster_pos(vp.pos).toTuple() for vp in self.raster_snap_v_points}
        line_too_short = len(rastered_positions) != len(self.raster_snap_v_points)

        if self.non_connectable(snap_zone, vp):
            return 'invalid'
        elif line_too_short:
            return 'line_too_short'
        elif self.new_connectables(snap_zone, vp):
            return 'valid'
        else:
            return 'no_items'

    def snap_dock(self):
        """Snaps the view to the raster."""
        v_points = [vp for item in self.view.items for vp in item.v_points]
        for vp in v_points:
            snap_zone = self.snap_zone(vp)

            for to_vp in self.to_dockables(vp, snap_zone)[:1]:
                vp.set_pos(to_vp.pos, Change.snapped)
                if not vp.follows(to_vp):
                    self.dock(vp, to_vp)

            for from_vp in self.from_dockables(snap_zone, vp):
                from_vp.set_pos(vp.pos, Change.snapped)
                if not from_vp.follows(vp):
                    self.dock(from_vp, vp)

    def raster_snap(self):
        """Snaps the view to the raster if raster mode is enabled."""
        if self.model.raster_snap_mode and self.check_snap_permission():
            for vp in self.raster_snap_v_points:
                vp.set_pos(config.raster_pos(vp.pos), Change.raster_snapped)

    def avoid_invalid_positions(self):
        """Avoids invalid positions by moving the view back to last valid positions."""
        moved = False

        for vp in self.raster_snap_v_points:
            validation_result = self.validation(vp)

            while validation_result in ['invalid', 'line_too_short'] and vp.last_positions:
                vp.set_pos(vp.last_positions.pop(), Change.avoid_invalid)
                validation_result = self.validation(vp)
                moved = True

            # delete element when created on invalid positions
            if vp.last_positions == [] and validation_result == 'invalid':
                self.model.delete_element(self.ep(vp).elem_id)
                self.model.update()
                return False

            vp.last_positions = [vp.pos]  # save last valid position

        return moved

    def on_mouse_released(self, mouse_pos):
        """Applies raster snapping to the view if view is released by the mouse."""
        if self.is_just_created and self.check_snap_permission(False):
            self.snap_dock()
            self.raster_snap()
            self.snap_dock()

        elif self.position_has_changed:
            self.snap_dock()

        self.is_just_created = False

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_elements(self):
        """Reacts on changes on elements count and removes himself if view isn't present anymore."""
        if self.elem_id not in self.model.elements:
            self.remove()

    def on_positions(self):
        """Reacts on position changes."""
        with section_manager.pos_section:
            for ep in self.model.elem_ports(self.elem_id):
                v_point = self.vp(ep)
                v_point.pos = self.model.get_pos(ep)

    def on_drag(self):
        """Reacts on drag and drop."""
        if not self.model.selection_dragging and not self.model.force_dragging:
            if self.position_has_changed and self.check_snap_permission(True):
                self.raster_snap()
                if self.avoid_invalid_positions():
                    self.raster_snap()

            self.position_has_changed = False

    def on_selection(self):
        """Reacts on selection changes. Updates the views z-mode and visibility state."""
        if self.selected != (self.elem_id in self.model.selection):
            # block signals prevent side effects (Qt events back to model)
            self.scene.blockSignals(True)
            self.view.selected = self.selected = self.elem_id in self.model.selection
            dragable = self.model.mode != Mode.sim
            active = dragable and self.view.enabled and (self.view.selected or self.view.is_under_mouse)
            z_value = 1000 if active else 1

            if hasattr(self.view, 'lines'):
                for line in self.view.lines:
                    line.z_value = z_value

            if hasattr(self.view, 'endpoints'):
                for endpoint in self.view.endpoints:
                    endpoint.z_value = z_value
                    endpoint.visible = active

            if hasattr(self.view, 'icon'):
                self.view.icon.z_value = z_value + 1
            self.scene.blockSignals(False)

    def on_dockings(self):
        """Reacts on view docking."""
        for ep in self.model.elem_ports(self.elem_id):
            v_point = self.vp(ep)

            # apply new model dockings to group
            for to_ep in self.model.dockings_out(ep):
                to_vp = self.vp(to_ep)
                if not v_point.follows(to_vp):
                    self.dock(v_point, to_vp)

            # remove group dockings that are not in model
            for other_vp in v_point.extern_followers:
                other_ep = self.ep(other_vp)
                out_elem_ids = {e for e, _ in self.model.dockings_out(ep)}
                in_elem_ids = {e for e, _ in self.model.dockings_in(ep)}
                if other_ep and other_ep.elem_id not in out_elem_ids | in_elem_ids:
                    other_vp.unfix(v_point)

    def on_mode(self):
        """Reacts on mode changes. Updates the state of the view."""
        if self.model.mode == Mode.sim:
            self.view.enabled = True
        else:
            enabled = self.model.is_selectable(self.elem_id)

            # reset consumer and producer bars
            ep0 = ElemPort(self.elem_id, '0')
            self.view.set_consumer_bar_effect(QtGui.QColor(0, 0, 0), self.model.get_pos(ep0), 0, 0)
            self.view.set_producer_bar_effect(QtGui.QColor(0, 0, 0), self.model.get_pos(ep0), 0, 0)

            # reset ev icon
            comp = self.model.get_component(self.elem_id)
            if 'EV' in comp['type']:
                self.view.icon.icon_path = dataHandler.get_component_icon('ev+battery.svg')
                self.view.set_state_of_charge_bar(QtGui.QColor(0, 0, 0), self.model.get_pos(ep0), 0, 0)
                self.view.set_state_of_charge_tip_bg(QtGui.QColor(0, 0, 0), self.model.get_pos(ep0), 0, 0)

            color_strength = 0 if enabled else 0.6
            self.view.set_color_effect(QtGui.QColor(255, 255, 255), color_strength)
            self.view.enabled = enabled
            self.view.selected &= enabled

        if self.model.raster_snap_mode:
            self.raster_snap()

    def on_param(self):
        """Reacts on parameter changes."""
        if hasattr(self.view, 'icon'):
            elem = self.model.elements[self.elem_id]
            self.view.icon.icon_path = dataHandler.get_component_icon(elem['icon'])

    def change_ev_icon(self, value):
        """Changes the icon of an electric vehicle depending on state of charge and plugged-in state."""
        comp = self.model.get_component(self.elem_id)
        if 'EV' in comp['type']:
            if value > 0:
                self.view.icon.icon_path = dataHandler.get_component_icon('ev/ev_consumer.svg')
            elif value < 0:
                self.view.icon.icon_path = dataHandler.get_component_icon('ev/ev_producer.svg')
            else:
                self.view.icon.icon_path = dataHandler.get_component_icon('ev+battery.svg')

    def set_effect(self, view_or_item, effect, color=QtGui.QColor(0, 0, 0), value=0):
        """Applies heat value effects to the view.
        :param color: the color- or shadow-effect color
        :param value: value for bar width or opacity (0..1)
        """
        if effect == HeatValueEffectKeys.EFFECT_COLOR:
            view_or_item.set_color_effect(color, 1)

        elif effect == HeatValueEffectKeys.EFFECT_SHADOW:
            if self.model.get_component(self.elem_id)['drawing_mode'] == 'icon':
                blur_radius = np.interp(abs(value), [0, 0.001, 0.499, 0.5, 0.799, 0.8], [0, 10, 10, 25, 25, 50])
                view_or_item.set_shadow_effect(self.model.get_icon_color(self.elem_id), blur_radius, 0, 0)
                self.change_ev_icon(value)
            else:
                blur_radius = 25 if color.value() > 200 else 0
                view_or_item.set_shadow_effect(color, blur_radius, 0, 0)

        elif effect == HeatValueEffectKeys.EFFECT_BAR:
            width = np.interp(abs(value), [0, 1], [0, 38])
            height = 5 if width else 0
            ep0 = ElemPort(self.elem_id, '0')
            pos = self.model.get_pos(ep0)

            # draw consumer or producer bar
            if value > 0:
                view_or_item.set_consumer_bar_effect(self.model.get_icon_color(self.elem_id), pos, width, height)
            elif value < 0:
                view_or_item.set_producer_bar_effect(self.model.get_icon_color(self.elem_id), pos, width, height)
            else:
                view_or_item.clear_effects()
            self.change_ev_icon(value)

        elif effect == HeatValueEffectKeys.EFFECT_TRANSPARENCY:
            color_strength = np.interp(abs(value), [0, 1], [0.5, 0])
            view_or_item.set_color_effect(QtGui.QColor(255, 255, 255), color_strength)
            self.change_ev_icon(value)

    def on_attrs(self):
        """Reacts on value changes of attributes. Triggers applying of heat value effects to the view."""
        if self.model.program_mode == ProgramMode.composition or not self.model.sim_progress:
            return

        comp = self.model.get_component(self.elem_id)

        if self.cfg[ConfigKeys.SIMULATION_SETTINGS][ConfigKeys.IS_HEAT_VALUE_EFFECT_FOR_GRIDS_ENABLED]:
            lines_heat_effect = self.cfg[ConfigKeys.SIMULATION_SETTINGS][ConfigKeys.HEAT_VALUE_EFFECT_GRIDS]

            if {'Branch', 'PQBus'} & set(comp['type']):
                u = abs(self.model.get_u_heat_value(self.elem_id))
                i = self.model.get_i_heat_value(self.elem_id)
                u_norm = np.interp(u, [0.05, 0.08, 0.1], [0, 0.5, 1])
                i_norm = np.interp(i, [0.8, 0.9, 1], [0, 0.5, 1])
                color = ct.color_interp(max(i_norm, u_norm), [0, 0.5, 1], [Qt.black, Qt.yellow, Qt.red])

                self.set_effect(self.view, lines_heat_effect, color)

            elif 'Transformer' in comp['type']:
                p, s = self.model.get_p_level(self.elem_id)  # p_level_primary, p_level_secondary
                color_primary = ct.color_interp(p, [0.01, 0.05, 0.1], [Qt.black, Qt.yellow, Qt.red])
                color_secondary = ct.color_interp(s, [0.01, 0.05, 0.1], [Qt.black, Qt.yellow, Qt.red])

                self.set_effect(self.view.line_left, lines_heat_effect, color_primary)
                self.set_effect(self.view.line_right, lines_heat_effect, color_secondary)

        if self.cfg[ConfigKeys.SIMULATION_SETTINGS][ConfigKeys.IS_HEAT_VALUE_EFFECT_FOR_CPP_ENABLED]:
            icons_heat_effect = self.cfg[ConfigKeys.SIMULATION_SETTINGS][ConfigKeys.HEAT_VALUE_EFFECT_CPP]

            if {'House', 'PV', 'CHP', 'WECS', 'EV'} & set(comp['type']):
                p_level = self.model.get_p_level(self.elem_id)
                self.set_effect(self.view, icons_heat_effect, value=p_level)

                if 'EV' in comp['type']:  # draw state of charge bar
                    soc = self.model.get_state_of_charge(self.elem_id)
                    width = np.interp(abs(soc), [0, 0.95], [0, 23])
                    height = 8 if width else 0
                    ep0 = ElemPort(self.elem_id, '0')
                    pos = self.model.get_pos(ep0)

                    if soc > 0.95:
                        self.view.set_state_of_charge_bar(QtGui.QColor(0, 255, 0), pos, width, height)
                        self.view.set_state_of_charge_tip(QtGui.QColor(0, 255, 0), pos, 2, 2)
                        self.view.set_state_of_charge_tip_bg(QtGui.QColor(185, 185, 185), pos, 2, 2)
                    else:
                        self.view.set_state_of_charge_bar(QtGui.QColor(0, 255, 0), pos, width, height)
                        self.view.set_state_of_charge_tip_bg(QtGui.QColor(185, 185, 185), pos, 2, 2)