import os

from PySide import QtGui

from maverig.presenter import abstractPresenter
from maverig.models.model import ProgramMode
from maverig.data import config, dataHandler
from maverig.data.config import ConfigKeys


class PropertyPanelPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the property panel."""

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the property panel presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super(PropertyPanelPresenter, self).__init__(presenter_manager, model, cfg)

        self.model.language_event += self.on_language
        self.model.selection_event += self.on_selection
        self.model.param_event += self.on_param
        self.model.program_mode_event += self.on_program_mode

        self.elem_ids = []
        self.widget_param_names = dict()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_change_visibility_triggered(self):
        """Toggles the visibility of the property panel. Saves the visibility state in the config."""
        self.view.setHidden(not self.view.isHidden())
        self.presenter_manager.menu_bar_presenter.view.action_trigger_property_panel.setChecked(
            not self.view.isHidden())
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_PROPERTY_PANEL_VISIBLE] = not self.view.isHidden()
        config.write_config(self.cfg)
        self.model.settings_event.demand()
        self.model.update()

    def check_spinbox(self, widget, value):
        """Checks spinbox values."""
        param_name = self.widget_param_names[widget]

        elem = self.model.elements[self.elem_ids[0]]
        comp = self.model.get_component(self.elem_ids[0])
        data = comp['params'][param_name]
        elem_value = elem['params'][param_name]

        if data.get('accepted_values'):
            value_position = data['accepted_values'].index(elem_value)
            if value < elem_value:
                new_value = data['accepted_values'][value_position - 1]
                self.view.set_new_accepted_value(widget, new_value)
            elif value > elem_value:
                new_value = data['accepted_values'][value_position + 1]
                self.view.set_new_accepted_value(widget, new_value)

    def value_changed(self, widget, value):
        """Handles value changes of the properties."""

        if isinstance(widget, QtGui.QCheckBox):
            value = widget.isChecked()

        if isinstance(widget, QtGui.QComboBox):
            value = widget.currentText()

        param_name = self.widget_param_names[widget]

        if self.__validate_set_param(widget, param_name, value):
            self.view.set_parameter_style(widget, False)  # values are no longer shared - only one value exists
            for elem_id in self.elem_ids:
                self.model.set_param_value(elem_id, param_name, value)
            self.model.update()

            # update the property panel in case that a new icon has been initialized
            if param_name == 'datafile':
                filename = dataHandler.get_normpath(value)
                for elem_id in self.elem_ids:
                    elem = self.model.elements[elem_id]
                    comp = self.model.get_component(elem_id)
                    if 'House' in comp['type'] and os.path.isfile(filename):
                        self.view.create_property_icon(dataHandler.get_component_icon(elem['icon']), 0)
                        self.view.change_household_cell(0, elem['params']['num_hh'])

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_language(self):
        """Reacts on language changes. Triggers view reinitialization so that the view adopts the chosen language."""
        self.view.init_ui()

    def on_selection(self):
        """Reacts on selection changes. Triggers view reinitialization so that the view is updated depending on the
        selection."""
        self.elem_ids = self.model.selection.copy()
        self.view.init_selection_counter(len(self.elem_ids))
        self.__view_init_properties()

    def on_param(self):
        """Reacts on value changes in model and updates the view."""
        for widget, param_name in self.widget_param_names.items():
            elem = self.model.elements[self.elem_ids[0]]
            value = elem['params'][param_name]
            if isinstance(widget, QtGui.QLineEdit) and widget.text() != value:
                widget.setText(value)
            elif isinstance(widget, QtGui.QCheckBox) and widget.isChecked() != value:
                widget.setChecked(value)
            elif isinstance(widget, QtGui.QSpinBox) and widget.value() != value:
                widget.setValue(value)
            elif isinstance(widget, QtGui.QDoubleSpinBox) and widget.value() != value:
                widget.setValue(value)

            multi_value = self.model.param_is_multivalue(self.elem_ids, param_name)
            self.view.set_parameter_style(widget, multi_value)

    def on_program_mode(self):
        """Reacts on program mode changes. In the simulation program mode the property panel is hided while the panel
        is visible in the composition program mode if the user didn't hide it."""
        if self.model.program_mode == ProgramMode.composition:
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_PROPERTY_PANEL_VISIBLE])
        elif self.model.program_mode == ProgramMode.simulation:
            self.view.hide()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Helper -----------------------------------------------------------------------------------------------------------

    def __validate_set_param(self, widget, param_name, value):
        """Validates if a property can be set to the given value."""
        comp = self.model.get_component(self.elem_ids[0])
        data = comp['params'][param_name]

        if param_name is 'l' and value == 0:
            self.presenter_manager.status_bar_presenter.error(config.ZERO_KM_LENGTH())
            return False

        if data.get('accepted_values') and value not in data['accepted_values']:
            self.view.change_color(widget, 'red')
            return False
        else:
            self.view.change_color(widget, 'white')
            return True
        return False

    def __view_init_properties(self):
        """Initializes property panel according to the current parameters in 'self.params'."""
        self.view.clear_prop_grid()
        self.widget_param_names = dict()

        # now initialize the content and check the given data types
        row = 0
        for elem_id in self.elem_ids:
            elem = self.model.elements[elem_id]
            comp = self.model.get_component(elem_id)
            if 'House' in comp['type']:
                self.view.create_property_icon(dataHandler.get_component_icon(elem['icon']), row)
                widget = self.view.create_household_cell(row, elem['params']['num_hh'])
                row += 1

        if self.elem_ids:
            elem = self.model.elements[self.elem_ids[0]]
            comp = self.model.components[elem['sim_model']]

        for param_name in self.model.get_shared_published_params(self.elem_ids):
            # property name
            data = comp['params'][param_name]
            value = elem['params'][param_name]
            accepted_values = data.get('accepted_values')

            self.view.create_property_label(data['caption'], row)
            # property value
            if data['datatype'] == 'int':
                widget = self.view.create_integer_property_cell(data['caption'], value, row, accepted_values)
            elif data['datatype'] == 'float':
                widget = self.view.create_float_property_cell(data['caption'], value, row, accepted_values)
            elif data['datatype'] == 'bool':
                widget = self.view.create_boolean_property_cell(data['caption'], value, row)
            elif data['datatype'] == 'file (*.csv)':
                widget = self.view.create_file_property_cell(data['caption'], value, row)
            elif data['datatype'] == 'string':
                widget = self.view.create_str_property_cell(data['caption'], value, row, accepted_values)

            self.widget_param_names[widget] = param_name

            multi_value = self.model.param_is_multivalue(self.elem_ids, param_name)
            self.view.set_parameter_style(widget, multi_value)
            row += 1