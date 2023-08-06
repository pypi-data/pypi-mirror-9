from datetime import datetime

from PySide import QtCore

from maverig.presenter import abstractPresenter
from maverig.data import config, dataHandler
from maverig.utils import numTools
from maverig.views import dialogs


class ComponentWizardPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the component wizard."""

    def __init__(self, presenter_manager, model, cfg):
        """Initialize the component wizard presenter.

        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        """
        super(ComponentWizardPresenter, self).__init__(presenter_manager, model, cfg)

        self.component_name = None

    def get_simulator_names(self):
        return self.model.simulators.keys()

    def get_category_names(self):
        """Read the names of the categories.

        :return: a sorted list with the names of the categories
        """
        categories = set()
        for component in self.model.components.values():
            categories.add(component['category'])
        return sorted(categories)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_new_simulator_triggered(self):
        """Triggers the visibility of the attribute panel."""
        self.view.init_new_simulator_gui()

    """ Link the view to this presenter """

    def init_view(self, v):
        self.view = v

    def on_add_simulator_triggered(self):
        """ save new simulator description in json """
        # simulator description dict (see maverig/data/components/simulators/*.json examples)
        params_table = self.view.table_simulator_params

        new_simulator = {
            'name': self.view.l_edit_simulator_name.text(),
            'starter': self.view.c_box_simulator_starter.currentText(),
            'address': self.view.l_edit_simulator_address.text(),
            'params': {
                params_table.text(row, 0): numTools.convert(params_table.text(row, 1))
                for row in range(params_table.rowCount())
                if params_table.text(row, 0)
            },
            'on_sim_init_parents': None  # LOW PRIORITY TODO: maybe add init_parents support like on_sim_init above
        }

        filename = dataHandler.get_normpath('maverig/data/components/simulators/%s.json'
                                            % self.view.l_edit_simulator_name.text(), create_dir=True)
        config.write_json(filename, new_simulator)

        self.view.new_simulator_dialog.close()
        self.model.simulators = config.read_simulators()  # refresh model simulators
        self.view.simulator_update()

    def on_add_component(self):
        """ save new component description in json """
        sim_name = self.view.intro_page.c_box_simulator.currentText()
        model_name = self.view.intro_page.l_edit_name.text()

        sim_model = sim_name + '.' + model_name

        c_box_icon = self.view.intro_page.c_box_icon
        icon = c_box_icon.itemData(c_box_icon.currentIndex())

        drawing_mode = self.view.intro_page.c_box_drawing.currentText()

        # TODO add GUI list items for ingoing and outgoing dockable component types (string array)
        in_types = ['Component']  # temporary solution: allow any connection
        out_types = ['Component']  # see 'type' in component descriptions in maverig/data/components

        if drawing_mode == 'icon':
            docking_ports = {
                '0': {'in': in_types},
                '1': {'out': out_types}
            }
        elif drawing_mode == 'node':
            docking_ports = {
                '0': {'in': in_types}  # TODO disable GUI out-list
            }
        elif 'line' in drawing_mode:
            docking_ports = {
                '0': {'out': out_types},  # TODO: disable GUI in-list
                '1': {'out': out_types}
            }

        param_tabs = self.view.attribute_parameter_page.param_tabs
        param_widgets = [param_tabs.widget(i) for i in range(param_tabs.count())
                         if param_tabs.widget(i).l_edit_parameter_name.text()]

        attr_tabs = self.view.attribute_parameter_page.attr_tabs
        attr_widgets = [attr_tabs.widget(i) for i in range(attr_tabs.count())
                        if attr_tabs.widget(i).l_edit_attribute_name.text()]

        # component description dict (see maverig/data/components/*.json examples)
        new_component = {
            'creation_time': datetime.now().isoformat(),

            'sim_model': sim_model,

            'type': ['Component', sim_name, model_name],  # types are like tags for abstract generalizations of groups
            'category': self.view.intro_page.c_box_category.currentText(),
            'tooltip': self.view.intro_page.l_edit_desc.text(),

            'icon': icon,
            'drawing_mode': drawing_mode,

            'docking_ports': docking_ports,

            # TODO: maybe add python-code text-edit fields and store methods in maverig.data.components.utils.%s.py
            # see maverig/data/components/utils/simInit.py for method examples
            # 'on_sim_init': 'maverig.data.components.utils.%s:on_sim_init_%s' % (short_name, short_name),
            #'on_set_param': 'maverig.data.components.utils.%s:on_set_param_%s' % (short_name, short_name),
            # TODO: otherwise leave empty
            'on_sim_init': '',
            'on_set_param': '',

            # TODO: add support for unpublished params if python-code-text-edit support had been added
            # published params or attrs are important as order indicator
            'published_params': [param.l_edit_parameter_name.text() for param in param_widgets],
            'published_attrs': [attr.l_edit_attribute_name.text() for attr in attr_widgets],


            'params': {
                param.l_edit_parameter_name.text(): {
                    'caption': param.l_edit_parameter_caption.text(),
                    'datatype': param.c_box_parameter_datatype.currentText(),
                    'accepted_values': [numTools.convert(param.table_parameter_accepted.text(i, 0),
                                                         param.c_box_parameter_datatype.currentText())
                                        for i in range(param.table_parameter_accepted.rowCount())
                                        if param.table_parameter_accepted.text(i, 0) != ''],
                    'default_value': numTools.convert(param.l_edit_default.text(),
                                                      param.c_box_parameter_datatype.currentText()),
                } for param in param_widgets
            },

            # TODO: add GUI support for 'out'/'in' string arrays (could also be left out first)
            'attrs': {
                attr.l_edit_attribute_name.text(): {
                    'caption': attr.l_edit_attribute_caption.text(),
                    'unit': attr.l_edit_attribute_unit.text(),
                    'static': attr.c_box_static.checkState() == QtCore.Qt.Checked,
                    #'out': attr.out_names,  # different-named attrs that this attribute may connect to, e.g. ['P_in']
                    #'in': attr.in_names  # different-named attrs that may connect to this attribute to, e.g. ['P_out']
                } for attr in attr_widgets
            }
        }

        if sim_model not in self.model.components.keys():
            # save new component description as json
            filename = dataHandler.get_normpath('maverig/data/components/%s.json' % sim_model, create_dir=True)
            config.write_json(filename, new_component)
            # refresh model components and component panel
            self.model.components = config.read_components()
            self.model.update()
            self.view.close()
        else:
            msg_box = dialogs.element_already_exist(sim_model)
            msg_box.exec_()

    def on_close_wizard(self):
        """Whenever the dialog gets closed (cancel, finish or close event)"""
        self.model.switch_modes(self.model.mode, self.model.mode)
        self.model.update()