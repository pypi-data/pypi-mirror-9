import sys
from datetime import datetime

from PySide import QtCore

from maverig.data import config, dataHandler
from maverig.data.config import RASTER_SIZE, ConfigKeys
from maverig.models.model import Mode, ProgramMode
from maverig.presenter.utils.forceEngine import ForceEngine
from maverig.presenter import abstractPresenter
from maverig.presenter.group_presenter.abstractGroupPresenter import scene_mapping
from maverig.presenter.group_presenter.nodeGroupPresenter import NodeGroupPresenter
from maverig.presenter.group_presenter.iconGroupPresenter import IconGroupPresenter
from maverig.presenter.group_presenter.lineGroupPresenter import LineGroupPresenter
from maverig.presenter.group_presenter.lineIconGroupPresenter import LineIconGroupPresenter
from maverig.views.groups.nodeGroup import NodeGroup
from maverig.views.groups.iconGroup import IconGroup
from maverig.views.groups.lineGroup import LineGroup
from maverig.views.groups.lineIconGroup import LineIconGroup
from maverig.views.positioning.vPoint import Change, VPMouse, Changes
from maverig.views import dialogs


class ScenarioPanelPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the scenario panel."""

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the scenario panel presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super().__init__(presenter_manager, model, cfg)

        # Allow recursion-depth > 1000 for dependent virtual point adjustments when moving big scenarios
        sys.setrecursionlimit(100000)

        self.line_taken = False
        self.line_start_pos = None

        self.model.mode_event += self.on_mode
        self.model.drag_event += self.on_drag
        self.model.attrs_event += self.on_attrs
        self.model.elements_event += self.on_elements
        self.model.error_event += self.on_error
        self.start = True

        self.model.init_history()
        self.vp_mouse = VPMouse()
        self.force_engine = None

        self.elem_branches = []

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def adjust_scene_rect(self):
        """Fits the size of the scene to the elements bounding rect."""
        items_bounding_rect = self.view.scene.itemsBoundingRect()
        # keep some margin to the edges
        items_bounding_rect.adjust(-15, -15, 15, 15)
        frame_rect = self.view.mapToScene(self.view.frameRect()).boundingRect()
        if self.start:
            frame_rect.adjust(1, 1, -1, -1)
            self.start = False
        scene_rect = frame_rect | items_bounding_rect
        self.view.scene.setSceneRect(scene_rect)

    def on_selection_changed(self):
        """Adopts selection changes in model. Adapts visibility and z-mode of elements."""
        selection = []
        selection_set = set()

        for graphics_item in self.view.scene.selectedItems():
            if graphics_item and hasattr(graphics_item, 'related_item'):
                elem_id = self.__get_elem_id(graphics_item)
                if elem_id not in selection_set:
                    selection_set.add(elem_id)
                    selection.append(elem_id)

        self.model.selection = selection
        self.model.update()

    def on_context_menu(self, event):
        """Creates and opens a context menu when the user performs a right mouse click in the scenario panel."""
        if not self.model.selection_dragging:
            is_composition = self.model.program_mode == ProgramMode.composition

            context_menu = self.view.create_context_menu()
            self.view.action_cut.setEnabled(is_composition and len(self.model.selection) > 0)
            self.view.action_copy.setEnabled(is_composition and len(self.model.selection) > 0)
            self.view.action_paste.setEnabled(is_composition and len(self.model.clipboard_elements) > 0)
            self.view.action_delete.setEnabled(is_composition and len(self.model.selection) > 0)
            self.view.action_select_all.setEnabled(len(self.model.elements) > 0)
            context_menu.popup(event.globalPos())

    def on_draw_background(self, painter):
        """Triggers raster drawing if raster mode is enabled."""
        if self.model.raster_mode:
            self.view.draw_raster(RASTER_SIZE, painter)

    def element_at(self, mouse_pos):
        """Returns element at the current mouse position."""
        graphics_item = self.view.scene.itemAt(mouse_pos)
        if graphics_item and hasattr(graphics_item, 'related_item'):
            return self.model.elements[self.__get_elem_id(graphics_item)]
        return None

    def create_new_element(self, mouse_pos):
        """Creates a new element at the given mouse position."""
        self.model.selection = []

        elem_id = self.model.create_element(self.model.comp, mouse_pos)
        self.model.update()

        vp0 = scene_mapping[self.view.scene][(elem_id, '0')]
        vp1 = scene_mapping[self.view.scene].get((elem_id, '1'))

        group_presenter = vp0.parent_item.parent_group.associated_presenter

        vp0_invalid = group_presenter.validation(vp0) == 'invalid'
        select_vp = vp0 if vp0_invalid or not vp1 else vp1

        if vp0_invalid and (not vp1 or group_presenter.validation(vp1) == 'invalid'):
            # abort creation on invalid position
            self.model.delete_element(elem_id)
            self.model.update()
            self.presenter_manager.status_bar_presenter.error(config.CREATION_INVALID())
        else:
            # select and drag item of last port (usually an endpoint)
            self.presenter_manager.mode_panel_presenter.view.setDisabled(True)
            select_vp.parent_item.selected = True

            # only start line dragging on mouse click (NOT on load/undo/redo)
            if vp1:
                self.line_taken = True
                self.line_start_pos = mouse_pos
            self.model.selection_dragging = True

        self.model.update()

    def mouse_clicked(self, mouse_pos, button):
        """Triggers creation of a new element at the given mouse position by clicking left mouse button. Switches between
        selection mode and component mode by clicking right mouse button."""
        if self.model.selection_dragging or self.model.mode == Mode.sim:
            return

        if button == QtCore.Qt.LeftButton:
            self.model.selection_dragging = self.model.is_selectable(self.element_at(mouse_pos))

            if self.model.mode == Mode.comp and not self.model.selection_dragging:
                self.create_new_element(mouse_pos)

        elif button == QtCore.Qt.RightButton:
            if not self.model.selection and self.element_at(mouse_pos):
                self.model.selection = [self.element_at(mouse_pos)['elem_id']]

        self.model.update()

    def damped_mouse_pos(self, mouse_pos):
        """Returns the damped mouse position if it is out of frame rect."""
        delta = mouse_pos - self.vp_mouse.pos

        # slow down mouse if it is out of frame rect
        frame_rect = self.view.mapToScene(self.view.frameRect()).boundingRect()
        if not frame_rect.contains(mouse_pos):
            length = QtCore.QLineF(QtCore.QPointF(), delta).length()
            delta = delta / length * 10  # move maximum 10 pixel when mouse is out of frame rect
            return self.vp_mouse.pos + delta
        return mouse_pos

    def mouse_moved(self, mouse_pos, buttons):
        """Sets mouse position based on the damped mouse position."""
        mouse_pos = self.damped_mouse_pos(mouse_pos)

        self.vp_mouse.set_pos(mouse_pos, Change.moved)
        if self.model.selection_dragging:
            self.view.ensureVisible(QtCore.QRectF(mouse_pos, mouse_pos))

    def mouse_released(self, mouse_pos):
        """Draws second endpoint of a line."""
        if self.line_taken and config.raster_pos(self.line_start_pos) != config.raster_pos(mouse_pos):
            self.line_taken = False
            self.line_start_pos = None

        if not self.line_taken:
            # send internal mouse_release for any selected group or group under mouse
            for group in self.groups:
                if group.selected:  # or group.is_under_mouse:
                    group.mouse_released(mouse_pos)
                    self.presenter_manager.mode_panel_presenter.view.setDisabled(False)

            self.model.selection_dragging = False
            self.model.update()
            self.model.add_history_point()

    def zoom(self, zoom_in, wheel_event=None):
        """Scales up or scales down the scenario depending on the mouse wheel alpha."""
        scale_factor = config.SCALE_FACTOR
        max_scale_distance = self.view.matrix().scale(scale_factor, scale_factor).mapRect(
            QtCore.QRectF(0, 0, 1, 1)).width()
        if zoom_in and not max_scale_distance > config.UPPER_SCALE_DISTANCE:
            self.view.scale(scale_factor, scale_factor)
            if not wheel_event and len(self.view.scene.selectedItems()) > 0:
                len_selected_items = len(self.view.scene.selectedItems())
                x = 0
                y = 0
                for graphics_item in self.view.scene.selectedItems():
                    x += graphics_item.x()
                    y += graphics_item.y()
                self.view.centerOn(x / len_selected_items, y / len_selected_items)
        elif not zoom_in and not max_scale_distance < config.LOWER_SCALE_DISTANCE:
            self.view.scale(1.0 / scale_factor, 1.0 / scale_factor)

    def zoom_fit(self):
        """Fits all elements into the view."""
        items_bounding_rect = self.view.scene.itemsBoundingRect()
        items_bounding_rect.adjust(-20, -20, 20, 20)
        self.view.fitInView(items_bounding_rect, QtCore.Qt.KeepAspectRatio)

    def delete_selected_elements(self):
        """Removes all selected elements."""
        for elem_id in self.model.selection.copy():
            self.model.delete_element(elem_id)
        self.model.update()
        self.model.add_history_point()

    def copy_selected_elements(self):
        """Copies all selected elements."""
        self.model.copy_to_clipboard(self.model.selection)

        # move clipboard elements
        for elem in self.model.clipboard_elements.values():
            for docking_port in elem['docking_ports'].values():
                pos = QtCore.QPointF(*docking_port['pos']) - QtCore.QPointF(4.000000, -4.000000)
                docking_port['pos'] = pos.toTuple()

        self.model.update()

    def cut_selected_elements(self):
        """Cuts all selected elements."""
        self.model.copy_to_clipboard(self.model.selection)
        self.delete_selected_elements()
        self.model.update()

    def paste_elements(self):
        """Pastes all copied elements and selects them."""
        self.model.selection = self.model.paste_from_clipboard()
        self.model.add_history_point()
        self.model.update()

        for group_presenter in self.group_presenters:
            if group_presenter.selected:
                group_presenter.deny_snap_pasted_elem = True
        # copy inserted elements: move elements again on next paste
        self.copy_selected_elements()

    def select_all_elements(self):
        """Selects all elements."""
        self.model.selection = [elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)]
        self.model.update()

    def select_all_active_elements(self, mouse_pos):
        """Selects all elements depending on the current active mode."""
        active_elem = self.element_at(mouse_pos)
        if active_elem:
            self.model.selection = [elem_id for elem_id, elem in self.model.elements.items()
                                    if active_elem['sim_model'] == elem['sim_model'] and self.model.is_selectable(elem)]
            self.model.update()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_attrs(self):
        """Reacts on value changes of attributes. Updates the background visualization of the date time if day and
        night visualization is enabled."""
        if self.model.program_mode != ProgramMode.composition and \
                self.cfg[ConfigKeys.SIMULATION_SETTINGS][ConfigKeys.IS_DAY_NIGHT_VIS_ENABLED]:
            time = self.model.sim_timestamp.time()
            hour = self.model.sim_timestamp.hour
            modulo = hour % 9

            if time == datetime.strptime("00:00:00", "%H:%M:%S").time():
                self.view.paint_datetime(195, 195)
            elif datetime.strptime("00:00:00", "%H:%M:%S").time() < time <= datetime.strptime("07:00:00",
                                                                                              "%H:%M:%S").time():
                bgcolor_from = 198 + ((modulo - 1) * 3)
                bgcolor_to = 198 + (modulo * 3)
                self.view.paint_datetime(bgcolor_from, bgcolor_to)
            elif time >= datetime.strptime("19:00:00", "%H:%M:%S").time():
                bgcolor_from = 216 - ((modulo - 1) * 3)
                bgcolor_to = 216 - (modulo * 3)
                self.view.paint_datetime(bgcolor_from, bgcolor_to)
            else:
                self.view.paint_datetime(219, 219)
        elif self.model.program_mode != ProgramMode.composition and not \
                self.cfg[ConfigKeys.SIMULATION_SETTINGS][ConfigKeys.IS_DAY_NIGHT_VIS_ENABLED]:
            self.view.paint_datetime(219, 219)

    def on_mode(self):
        """Reacts on mode changes. Updates the views drag mode, interactive mode and mouse cursor depending on the
        active mode."""
        if self.model.mode == Mode.hand:
            self.view.setDragMode(self.view.ScrollHandDrag)
            self.view.setInteractive(False)
        elif self.model.mode == Mode.selection:
            self.view.setDragMode(self.view.RubberBandDrag)
            self.view.setCursor(QtCore.Qt.ArrowCursor)
            self.view.setInteractive(True)
        elif self.model.mode == Mode.sim:
            self.view.setDragMode(self.view.RubberBandDrag)
            self.view.setCursor(QtCore.Qt.ArrowCursor)
            self.view.setInteractive(True)
        else:
            self.view.setDragMode(self.view.NoDrag)
            self.view.setCursor(QtCore.Qt.CrossCursor)
            self.view.setInteractive(True)

    def on_drag(self):
        """Reacts if an element is dragged into the scene from the component panel."""
        if self.model.selection_dragging:
            selected_items = {graphics_item.related_item
                              for graphics_item in self.view.scene.selectedItems()
                              if hasattr(graphics_item, "related_item")}
            for item in selected_items:
                item.vp_movable.follow(self.vp_mouse, Changes.all, Change.moved, True)
        else:
            for vp in self.vp_mouse.followers.copy():
                vp.unfollow(self.vp_mouse)

    def on_elements(self):
        """Reacts on changes on elements count and updates the view."""
        ids_view = set({self.__get_elem_id(graphics_item)
                        for graphics_item in self.view.items() if hasattr(graphics_item, 'related_item')})
        ids_model = set(self.model.elements)

        ids_to_add = ids_model - ids_view
        for elem_id in ids_to_add:
            self.__view_add_element(elem_id)

    def on_error(self, title, text, info_text, elem_ids):
        """Reacts on model scenario errors and displays an error dialog """
        dialogs.error_dialog(title, text, info_text)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Helper -----------------------------------------------------------------------------------------------------------

    def __view_add_element(self, elem_id):
        """Adds an element to the scene."""
        elem = self.model.elements[elem_id]
        comp = self.model.get_component(elem_id)

        elem_positions = {ep.port: self.model.get_pos(ep) for ep in self.model.elem_ports(elem_id)}
        if comp['drawing_mode'] == "line":
            presenter = LineGroupPresenter(self.presenter_manager, self.model, elem_id, self.cfg)
            view = LineGroup(elem_positions)
        elif comp['drawing_mode'] == "line-icon-line":
            presenter = LineIconGroupPresenter(self.presenter_manager, self.model, elem_id, self.cfg)
            view = LineIconGroup(elem_positions, dataHandler.get_component_icon(elem['icon']))
        elif comp['drawing_mode'] == "icon":
            presenter = IconGroupPresenter(self.presenter_manager, self.model, elem_id, self.cfg)
            view = IconGroup(elem_positions, dataHandler.get_component_icon(elem['icon']))
        elif comp['drawing_mode'] == "node":
            presenter = NodeGroupPresenter(self.presenter_manager, self.model, elem_id, self.cfg)
            view = NodeGroup(elem_positions)

        presenter.view = view
        view.associated_presenter = presenter
        view.init_view(self.view.scene)
        presenter.init_scene_mapping(self.view.scene)

    def run_force_layout(self):
        """Triggers running of the force atlas algorithm."""
        self.force_engine = ForceEngine(self, self.model, self.view.scene)

    def __get_elem_id(self, graphics_item):
        """Returns the element id for the given graphics item."""
        return graphics_item.related_item.parent_group.associated_presenter.elem_id

    @property
    def group_presenters(self):
        """Returns a set of all group presenters."""
        return {graphics_item.related_item.parent_group.associated_presenter
                for graphics_item in self.view.scene.items()
                if hasattr(graphics_item, "related_item")}

    @property
    def groups(self):
        """Returns a set of all groups."""
        return {graphics_item.related_item.parent_group
                for graphics_item in self.view.scene.items()
                if hasattr(graphics_item, "related_item")}