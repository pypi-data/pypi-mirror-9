from maverig.models.model import ProgramMode
from maverig.data import config
from maverig.data.config import ConfigKeys
from maverig.utils import colorTools
from maverig.presenter import abstractPresenter


class AttributePanelPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the attribute panel."""

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the attribute panel presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super(AttributePanelPresenter, self).__init__(presenter_manager, model, cfg)

        self.model.language_event += self.on_language
        self.model.selection_event += self.on_selection
        self.model.attrs_event += self.on_attrs
        self.model.program_mode_event += self.on_program_mode

        self.sim_progress = self.model.sim_progress

        self.elem_ids = []  # a list of the selected element ids
        self.cells = dict()  # dict of attribute names to attribute cells

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_change_visibility_triggered(self):
        """Toggles the visibility of the attribute panel. Saves the visibility state in the config."""
        self.view.setHidden(not self.view.isHidden())
        self.presenter_manager.menu_bar_presenter.view.action_trigger_attribute_panel.setChecked(
            not self.view.isHidden())
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_ATTRIBUTE_PANEL_VISIBLE] = not self.view.isHidden()
        config.write_config(self.cfg)

    def on_change_graph_visibility_triggered(self, name):
        """Toggles the visibility of the different graphs in the attribute panel."""
        self.cfg[ConfigKeys.UI_STATE].setdefault(ConfigKeys.ATTRIBUTE_GRAPHS_VISIBLE, [])
        attribute_graphs_visible = self.cfg[ConfigKeys.UI_STATE][ConfigKeys.ATTRIBUTE_GRAPHS_VISIBLE]

        if name in attribute_graphs_visible:
            attribute_graphs_visible.remove(name)
        else:
            attribute_graphs_visible.append(name)
        self.update_graph_visibility(name)
        config.write_config(self.cfg)
        self.model.settings_event.demand()
        self.model.update()

    def update_graph_visibility(self, name):
        """Saves the visible graphs in the config."""
        cell = self.cells[name]
        self.cfg[ConfigKeys.UI_STATE].setdefault(ConfigKeys.ATTRIBUTE_GRAPHS_VISIBLE, [])
        attribute_graphs_visible = self.cfg[ConfigKeys.UI_STATE][ConfigKeys.ATTRIBUTE_GRAPHS_VISIBLE]
        cell.set_graph_visibility(name in attribute_graphs_visible)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_language(self):
        """Reacts on language changes. Triggers view reinitialization so that the view adopts the chosen language."""
        # TODO refresh info_label translation
        self.view.translate()
        for cell in self.cells.values():
            cell.translate()

    def on_selection(self):
        """Reacts on selection changes. Creates attribute cells for the attribute panel."""
        if self.model.program_mode != ProgramMode.composition:
            self.elem_ids = self.model.selection.copy()
            if self.elem_ids:
                self.__init_attributes()
                self.on_attrs()
            else:
                self.cells.clear()
                self.view.clear_container()

    def on_attrs(self):
        """Reacts on value changes of attributes. Updates the displayed values in the attribute panel."""
        if self.model.program_mode != ProgramMode.composition:
            for attr_name, cell in list(self.cells.items()):
                if cell not in self.cells.values():
                    break
                content_params = {
                    'current_value': self.model.get_attr_value(self.elem_ids[0], attr_name),
                    'multivalue': self.model.attr_is_multivalue(self.elem_ids, attr_name),
                    'lines_values': [self.model.get_attr_values(elem_id, attr_name) for elem_id in self.elem_ids]
                }
                cell.change_content(**content_params)

    def on_program_mode(self):
        """Reacts on program mode changes. In the composition program mode the attribute panel is hided while the panel
        is visible in the simulation program mode if the user didn't hide it."""
        if self.model.program_mode == ProgramMode.composition:
            self.view.hide()
            self.cells.clear()
            self.view.clear_container()
        elif self.model.program_mode == ProgramMode.simulation:
            self.model.selection_event.demand()
            self.model.update()
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_ATTRIBUTE_PANEL_VISIBLE])

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Helper -----------------------------------------------------------------------------------------------------------

    def __init_attributes(self):
        """Initializes all shared attributes of the selected items."""
        self.view.create_attribute_panel()
        self.cells.clear()
        if self.model.program_mode != ProgramMode.composition:
            # use predefined color set
            base_colors = [self.model.get_icon_color(elem_id) for elem_id in self.elem_ids[:9]]
            # use colors taken from icon
            lines_colors = colorTools.distinct_colors(base_colors)

            for attr_name in self.model.get_shared_published_attrs(self.elem_ids):
                comp = self.model.get_component(self.elem_ids[0])
                data = comp['attrs'][attr_name]

                cell_params = {
                    'name': attr_name,
                    'caption': data.get('caption', ''),
                    'unit': data.get('unit', ''),
                    'lines_labels': self.elem_ids,
                    'lines_values': [self.model.get_attr_values(elem_id, attr_name) for elem_id in self.elem_ids],
                    'lines_colors': lines_colors,
                    'graph_available': not data['static'],
                    'step_size': int(self.model.sim_step_size / 60)
                }

                self.view.unit = data.get('unit', '')
                self.cells[attr_name] = self.view.create_attribute_cell(**cell_params)

                if not data['static']:
                    self.update_graph_visibility(attr_name)

            if not self.cells:
                self.view.update_info_label(True)