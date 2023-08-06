import locale
import gettext
from unittest import TestCase
import os

from PySide import QtCore
from maverig.data import config
from maverig.data import dataHandler
from datetime import timedelta
from maverig.models.model import Model, ElemPort, Mode, fast_deepcopy
from maverig.utils.scenarioErrors import ScenarioError


class TestModel(TestCase):
    def setUp(self):
        # install locale
        current_locale, encoding = locale.getdefaultlocale()
        locale_path = dataHandler.get_lang_path()
        language = gettext.translation(current_locale, locale_path, [current_locale])
        language.install()

        self.model = Model()

    def test_switch_modes(self):
        """Switches between the composition modes."""
        self.model.mode = Mode.comp
        self.model.switch_modes(Mode.comp, Mode.selection)

        assert self.model.mode == Mode.selection

        self.model.switch_modes(Mode.comp, Mode.selection)

        assert self.model.mode == Mode.comp

        self.model.switch_modes(Mode.hand, Mode.selection)

        assert self.model.mode == Mode.hand

    def test_is_selectable(self):
        """Checks for an item if it is selectable or not."""
        elem_id = self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        self.model.mode = Mode.selection

        assert self.model.is_selectable(elem_id)

        self.model.mode = Mode.hand

        assert not self.model.is_selectable(elem_id)

    def test_init_history(self):
        """Init the history if an empty scene is open."""
        scenario_0 = fast_deepcopy(self.model.scenario)
        self.model.init_history()

        assert self.model.history_redo == self.model.history_undo == []

        # undo and redo won't have any effect because history is empty
        self.model.undo()
        assert self.model.scenario == scenario_0
        self.model.redo()
        assert self.model.scenario == scenario_0

    def test_add_history_point(self):
        """Changes history after an action."""
        assert len(self.model.history_undo) == 0

        # element changes have an effect on history
        scenario_0 = fast_deepcopy(self.model.tmp_scenario_copy)
        elem_id = self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        self.model.add_history_point()

        assert self.model.tmp_scenario_copy != scenario_0
        assert len(self.model.history_undo) == 1

        # selection changes have no effect on history
        scenario_1 = fast_deepcopy(self.model.tmp_scenario_copy)
        self.model.selection = [elem_id]
        self.model.add_history_point()

        assert self.model.tmp_scenario_copy == scenario_1
        assert len(self.model.history_undo) == 1

    def test_undo(self):
        """Undo the last performed action."""
        scenario_0 = fast_deepcopy(self.model.scenario)

        assert len(self.model.history_undo) == 0

        # add history point: element creation will be a significant scenario change
        elem_id = self.model.create_element('PyPower.PQBus', QtCore.QPointF(150.0, 350.0))
        self.model.add_history_point()

        assert len(self.model.history_undo) == 1

        # selection changes will not add an history point
        self.model.selection = [elem_id]
        self.model.add_history_point()

        assert len(self.model.history_undo) == 1

        self.model.undo()

        assert len(self.model.history_undo) == 0
        assert self.model.scenario == scenario_0

    def test_redo(self):
        """Recover the last undone action."""
        assert len(self.model.history_redo) == 0

        # add history point: element creation will be a significant scenario change
        elem_id = self.model.create_element('PyPower.PQBus', QtCore.QPointF(150.0, 350.0))
        self.model.add_history_point()
        scenario_1 = fast_deepcopy(self.model.scenario)
        self.model.undo()

        assert len(self.model.history_redo) == 1

        self.model.redo()

        assert len(self.model.history_redo) == 0
        assert self.model.scenario == scenario_1

    def test_changes_count(self):
        """Summs up changes after an edit to the history."""
        assert self.model.changes_count() == 0

        self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))

        assert self.model.changes_count() == 1

    def test_copy_to_clipboard(self):
        """Copies all elements of the elem_ids list to an internal clipboard."""
        assert self.model.clipboard_elements == {}

        self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(300, 70))
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(200, 80))

        assert self.model.clipboard_elements == {}

        self.model.selection = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()
        self.model.copy_to_clipboard(self.model.selection)

        assert self.model.clipboard_elements != {}

    def test_paste_from_clipboard(self):
        """Paste all elements from internal clipboard and return the new elem_ids
        only dockings inside of clipboard will be maintained."""
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(300, 70))
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(200, 80))
        self.model.selection = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()
        self.model.copy_to_clipboard(self.model.selection)
        elem_ids = self.model.paste_from_clipboard()

        assert len(elem_ids) == 3

    def test_create_element(self):
        """Creates an element."""
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))

        assert len(self.model.elements) == 1

    def test_delete_element(self):
        """Deletes an element."""
        elem_id = self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))

        assert len(self.model.elements) == 1

        self.model.delete_element(elem_id)

        assert len(self.model.elements) == 0

    def test_get_shared_published_params(self):
        """Return a list of composed parameter instances which are contained in each element of elem_ids, e.g.::

            [NumResidents(), NumHouseHolds() ...]

        - parameter.value: the parameter value of the first element of elem_ids
        - parameter.shared_values: a list of values according to each element in elem_ids"""
        elem_ids = {elem_id for elem_id in self.model.elements}

        assert self.model.get_shared_published_params(elem_ids) == []

        self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(300, 70))
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(200, 80))
        self.model.selection = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()
        elem_ids = self.model.selection

        assert self.model.get_shared_published_params(elem_ids) != []

    def test_get_param_value(self):
        """Get value of parameter with param_name in element elem_id return None if param_name does not exist."""
        pv_1 = self.model.create_element("CSV.PV", QtCore.QPointF(400, 60))
        self.model.set_param_value(pv_1, 'datafile', os.path.normpath('maverig/tests/data/pv_30kw.small.csv'))
        pv_2 = self.model.create_element("CSV.PV", QtCore.QPointF(450, 30))
        self.model.set_param_value(pv_2, 'datafile', os.path.normpath('maverig/tests/data/pv_30kw.small.csv'))
        self.model.selection = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()
        elem_ids = self.model.selection

        for id in elem_ids:
            assert self.model.get_param_value(id, 'datafile') == os.path.normpath(
                'maverig/tests/data/pv_30kw.small.csv')
            assert self.model.get_param_value(id, 'other') is None

    def test_set_param_value(self):
        """Set value of parameter with param_name in element elem_id if value is not None."""
        elem_ids = {elem_id for elem_id in self.model.elements}

        assert self.model.get_shared_published_params(elem_ids) == []

        pv_1 = self.model.create_element("CSV.PV", QtCore.QPointF(400, 60))
        self.model.set_param_value(pv_1, 'datafile', os.path.normpath('maverig/tests/data/pv_30kw.small.csv'))
        pv_2 = self.model.create_element("CSV.PV", QtCore.QPointF(450, 30))
        self.model.set_param_value(pv_2, 'datafile', os.path.normpath('maverig/tests/data/pv_30kw.small.csv'))
        self.model.selection = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()

        elem_ids = self.model.selection

        for id in elem_ids:
            assert self.model.get_param_value(id, 'datafile') == os.path.normpath(
                'maverig/tests/data/pv_30kw.small.csv')
            assert self.model.get_param_value(id, 'other') is None

    def test_get_selected(self):
        """Get value of parameter with param_name in element elem_id return None if param_name does not exist."""
        self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        self.model.selection = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()
        elem_ids = self.model.selection

        for id in elem_ids:
            assert self.model.get_selected(id) is True

    def test_set_selected(self):
        """Sets selected-flag to marked elements."""
        el1 = self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        el2 = self.model.create_element("PyPower.RefBus", QtCore.QPointF(300, 70))
        elem_ids = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()

        for id in elem_ids:
            self.model.set_selected(id, elem_ids)
        el3 = self.model.create_element("PyPower.RefBus", QtCore.QPointF(340, 40))
        self.model.update()

        assert self.model.get_selected(el1) is True
        assert self.model.get_selected(el2) is True
        assert self.model.get_selected(el3) is False

    def test_docking_port(self):
        """Get the docking_port of an element."""
        elem_id = self.model.create_element("CSV.PV", QtCore.QPointF(400, 60))
        assert self.model.docking_port([elem_id, '0']) == {'pos': (400, 60), 'in': [], 'out': []}

    def test_get_pos(self):
        """Get the position of an element."""
        elem_id = self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))

        for ep in self.model.elem_ports(elem_id):
            assert self.model.get_pos(ep) == QtCore.QPointF(400, 60)

    def test_set_pos(self):
        """Set the position of an element."""
        elem_id = self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))

        for ep in self.model.elem_ports(elem_id):
            assert self.model.get_pos(ep) == QtCore.QPointF(400, 60)

        for ep in self.model.elem_ports(elem_id):
            self.model.set_pos(ep, QtCore.QPointF(300, 50))

        for ep in self.model.elem_ports(elem_id):
            assert self.model.get_pos(ep) == QtCore.QPointF(300, 50)

    def test_dockings_out(self):
        """Return an array of outgoing element ports."""
        refbus_1 = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200, 15))
        branch_1 = self.model.create_element("PyPower.Branch", QtCore.QPointF())
        self.model.set_pos([branch_1, '0'], QtCore.QPointF(200, 15))
        self.model.set_pos([branch_1, '1'], QtCore.QPointF(300, 60))
        bus_1 = self.model.create_element("PyPower.PQBus", QtCore.QPointF(300, 60))
        self.model.dock([branch_1, '0'], [refbus_1, '0'])
        self.model.dock([branch_1, '1'], [bus_1, '0'])

        assert self.model.dockings_out([branch_1, '0']) == [ElemPort(refbus_1, '0')]
        assert self.model.dockings_out([branch_1, '1']) == [ElemPort(bus_1, '0')]
        assert self.model.dockings_out([refbus_1, '0']) == []
        assert self.model.dockings_out([bus_1, '0']) == []

    def test_dockings_in(self):
        """Return an array of outgoing element ports."""
        refbus_1 = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200, 15))
        branch_1 = self.model.create_element("PyPower.Branch", QtCore.QPointF())
        self.model.set_pos([branch_1, '0'], QtCore.QPointF(200, 15))
        self.model.set_pos([branch_1, '1'], QtCore.QPointF(300, 60))
        bus_1 = self.model.create_element("PyPower.PQBus", QtCore.QPointF(300, 60))
        self.model.dock([branch_1, '0'], [refbus_1, '0'])
        self.model.dock([branch_1, '1'], [bus_1, '0'])

        assert self.model.dockings_in([branch_1, '0']) == []
        assert self.model.dockings_in([branch_1, '1']) == []
        assert self.model.dockings_in([refbus_1, '0']) == [ElemPort(branch_1, '0')]
        assert self.model.dockings_in([bus_1, '0']) == [ElemPort(branch_1, '1')]

    def test_can_dock(self):
        """Tests if one component may dock to another."""
        refbus_1 = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200, 15))
        branch_1 = self.model.create_element("PyPower.Branch", QtCore.QPointF())
        self.model.set_pos([branch_1, '0'], QtCore.QPointF(200, 15))
        self.model.set_pos([branch_1, '1'], QtCore.QPointF(300, 60))
        bus_1 = self.model.create_element("PyPower.PQBus", QtCore.QPointF(300, 60))

        assert self.model.can_dock([branch_1, '0'], [refbus_1, '0']) is True
        assert self.model.can_dock([refbus_1, '0'], [bus_1, '0']) is False

    def test_dock(self):
        """Docks branch elements to other elements, if allowed."""
        refbus_1 = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200, 15))
        branch_1 = self.model.create_element("PyPower.Branch", QtCore.QPointF())
        self.model.set_pos([branch_1, '0'], QtCore.QPointF(200, 15))
        self.model.set_pos([branch_1, '1'], QtCore.QPointF(300, 60))
        bus_1 = self.model.create_element("PyPower.PQBus", QtCore.QPointF(300, 60))
        self.model.dock([branch_1, '0'], [refbus_1, '0'])
        self.model.dock([branch_1, '1'], [bus_1, '0'])

        assert self.model.dockings_out([branch_1, '0']) == [ElemPort(refbus_1, '0')]
        assert self.model.dockings_in([branch_1, '0']) == []
        assert self.model.dockings_out([branch_1, '1']) == [ElemPort(bus_1, '0')]
        assert self.model.dockings_in([branch_1, '1']) == []

        assert self.model.dockings_out([refbus_1, '0']) == []
        assert self.model.dockings_in([refbus_1, '0']) == [ElemPort(branch_1, '0')]

        assert self.model.dockings_out([bus_1, '0']) == []
        assert self.model.dockings_in([bus_1, '0']) == [ElemPort(branch_1, '1')]

    def test_undock(self):
        """Undocks docked components."""
        refbus_1 = self.model.create_element('PyPower.RefBus', QtCore.QPointF(200, 15))
        branch_1 = self.model.create_element("PyPower.Branch", QtCore.QPointF())
        self.model.set_pos([branch_1, '0'], QtCore.QPointF(200, 15))
        self.model.set_pos([branch_1, '1'], QtCore.QPointF(300, 60))
        bus_1 = self.model.create_element("PyPower.PQBus", QtCore.QPointF(300, 60))
        self.model.dock([branch_1, '0'], [refbus_1, '0'])
        self.model.dock([branch_1, '1'], [bus_1, '0'])
        self.model.undock([branch_1, '0'], [refbus_1, '0'])
        self.model.undock([branch_1, '1'], [bus_1, '0'])

        assert self.model.dockings_out([branch_1, '0']) == []
        assert self.model.dockings_in([branch_1, '0']) == []
        assert self.model.dockings_out([branch_1, '1']) == []
        assert self.model.dockings_in([branch_1, '1']) == []

        assert self.model.dockings_out([refbus_1, '0']) == []
        assert self.model.dockings_in([refbus_1, '0']) == []

        assert self.model.dockings_out([bus_1, '0']) == []
        assert self.model.dockings_in([bus_1, '0']) == []

    def test_update(self):
        """Fires all events with pending demands."""
        self.counter = 0

        def on_elements():
            self.counter += 1
        self.model.update()

        assert self.counter == 0

        self.model.dockings_event += on_elements
        self.model.dockings_event.demand()
        self.model.update()

        assert self.counter == 1

    def test_update_all(self):
        """Fires all events."""
        self.counter = 0

        def on_elements():
            self.counter += 1
        self.model.update()

        assert self.counter == 0

        self.model.dockings_event += on_elements
        self.model.elements_event += on_elements
        self.model.positions_event += on_elements
        self.model.dockings_event.demand()
        self.model.update()

        assert self.counter == 1

        self.model.elements_event.demand()
        self.model.update()

        assert self.counter == 2

        self.model.positions_event.demand()
        self.model.elements_event.demand()
        self.model.update()

        assert self.counter == 4

    def test_deselect_all_elems(self):
        """Deselect all elements."""
        el1 = self.model.create_element("PyPower.RefBus", QtCore.QPointF(400, 60))
        el2 = self.model.create_element("PyPower.RefBus", QtCore.QPointF(300, 70))
        elem_ids = {elem_id for elem_id in self.model.elements if self.model.is_selectable(elem_id)}
        self.model.update()

        for id in elem_ids:
            self.model.set_selected(id, elem_ids)
        el3 = self.model.create_element("PyPower.RefBus", QtCore.QPointF(340, 40))
        self.model.update()

        assert self.model.get_selected(el1) is True
        assert self.model.get_selected(el2) is True
        assert self.model.get_selected(el3) is False
        assert len(self.model.selection) > 0

        self.model.deselect_all_elems()

        assert len(self.model.selection) == 0

    def test_copy(self):
        """Return new flat copied model including scenario, components and simulators descriptions
        and no connected events."""
        new_model = self.model.copy()

        assert new_model.sim_end == self.model.sim_end
        assert new_model.clipboard_elements == self.model.clipboard_elements

    def test_changes_count(self):
        """Return an int value representing the current model state changes counter."""
        self.model.create_element("PyPower.RefBus",QtCore.QPointF(100, 80))
        self.model.create_element('CSV.WECS', QtCore.QPointF(100, 60))
        self.model.create_element("PyPower.PQBus", QtCore.QPointF(100, 100))
        elem_id = self.model.create_element("PyPower.Branch", QtCore.QPointF(100, 120))

        # selection is not history specific and has no effect on changes count
        self.model.selection = [elem_id]

        assert self.model.changes_count() == 4

    def test_get_simulator(self):
        """Return the simulator of the given element."""
        refbus_1 = self.model.create_element('PyPower.RefBus', QtCore.QPointF(400, 60))
        pv_1 = self.model.create_element('CSV.PV', QtCore.QPointF(40, 60))

        assert self.model.get_simulator(refbus_1) is not self.model.get_simulator(pv_1)

    def test_get_icon_color(self):
        """Return the color od the given icon."""
        pv_1 = self.model.create_element('CSV.PV', QtCore.QPointF(40, 60))
        refbus_1 = self.model.create_element('PyPower.RefBus', QtCore.QPointF(45, 60))
        trafo_1 = self.model.create_element('PyPower.Transformer', QtCore.QPointF(100, 60))
        wecs_1 = self.model.create_element('CSV.WECS', QtCore.QPointF(100, 60))

        assert self.model.get_icon_color(pv_1) != self.model.get_icon_color(refbus_1)
        assert self.model.get_icon_color(trafo_1) == self.model.get_icon_color(refbus_1)
        assert self.model.get_icon_color(pv_1) == self.model.get_icon_color(wecs_1)

    def test_set_param_value(self):
        """Sets a parameter of an element to an given value."""
        house_1 = self.model.create_element('CSV.House', QtCore.QPointF(40, 60))
        self.model.set_param_value(house_1, 'num_hh', 4)
        assert self.model.get_param_value(house_1, 'num_hh') is 4

    def test_get_attr_values(self):
        """Return values of an attribute in a specific timestamp area."""
        pv_1 = self.model.create_element('CSV.PV', QtCore.QPointF(40, 600))
        self.model.set_param_value(pv_1, 'datafile', os.path.normpath('maverig/tests/data/pv_30kw.small.csv'))
        self.model.elements[pv_1]['attrs']['P'] = [0.75, 0.3, 0.8, 5, 8]

        assert self.model.get_attr_values(pv_1, 'P', 1, 4) == [0.3, 0.8, 5, 8]

    def test_get_attr_value(self):
        """Return a value of an attribute on an specific timestamp."""
        pv_1 = self.model.create_element('CSV.PV', QtCore.QPointF(40, 600))
        self.model.set_param_value(pv_1, 'datafile', os.path.normpath('maverig/tests/data/pv_30kw.small.csv'))
        self.model.elements[pv_1]['attrs']['P'] = [0.75, 0.3, 0.8]

        assert self.model.get_attr_value(pv_1, 'P', 1) == 0.3

    def test_get_u_heat_value(self):
        """Return the u_heat value from an element on a specific timestamp."""
        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))

        # add simulation data indices
        self.model.sim_timestamps = [self.model.sim_start+timedelta(seconds=self.model.sim_step_size*i)
                                     for i in range(12)]
        self.model.sim_index = 0

        assert self.model.get_u_heat_value('PyPower.PQBus_5') == -0.003734824225657185
        assert self.model.get_u_heat_value('PyPower.Branch_1') == -0.0015318751959563226

    def test_get_i_heat_value(self):
        """Return the i_heat value from an element on a specific timestamp."""
        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))

        # add simulation data indices
        self.model.sim_timestamps = [self.model.sim_start+timedelta(seconds=self.model.sim_step_size*i)
                                     for i in range(12)]
        self.model.sim_index = 0

        assert self.model.get_i_heat_value('PyPower.Branch_1') == 0.012083101074209113

    def test_get_p_level(self):
        """Return the p_level from an element on a specific timestamp."""
        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))

        # add simulation data indices
        self.model.sim_timestamps = [self.model.sim_start+timedelta(seconds=self.model.sim_step_size*i)
                                     for i in range(12)]
        self.model.sim_index = 0

        assert self.model.get_p_level('CSV.EV_1') == 1.0
        assert self.model.get_p_level('CSV.CHP_1') == -0.9152
        assert self.model.get_p_level('PyPower.Branch_1') == 0
        assert self.model.get_p_level('CSV.PV_3') == 0
        assert self.model.get_p_level('CSV.House_1') == 0.2169767441860465
        assert self.model.get_p_level('CSV.WECS_2') == -0.3351
        assert self.model.get_p_level('PyPower.Transformer_1') == (0.00028852887200153893, 0.027531669873983984)

    def test_get_state_of_charge(self):
        """Return the state of charge from an element on a specific timestamp."""
        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))

        # add simulation data indices
        self.model.sim_timestamps = [self.model.sim_start+timedelta(seconds=self.model.sim_step_size*i)
                                     for i in range(12)]
        self.model.sim_index = 0

        assert self.model.get_state_of_charge('CSV.EV_1') == 0.29

    def test_attr_is_multivalue(self):
        """Return True if an attribute is available in elem_ids."""
        pv_1 = self.model.create_element("CSV.PV", QtCore.QPointF(100, 80))
        self.model.set_param_value(pv_1, 'datafile', os.path.normpath('maverig/tests/data/pv_30kw.small.csv'))
        self.model.elements[pv_1]['attrs']['P'] = [1, 0.3, 0.8]
        wecs_1 = self.model.create_element('CSV.WECS', QtCore.QPointF(100, 60))
        self.model.set_param_value(pv_1, 'datafile', os.path.normpath('maverig/tests/data/wecs_10kw.small.csv'))
        self.model.elements[pv_1]['attrs']['P'] = [1, 0.3, 0.8]

        assert self.model.attr_is_multivalue([pv_1, wecs_1], 'P') is True

    def test_param_is_multivalue(self):
        """Return whether parmeter values differ in elements of elem_ids."""
        house_1 = self.model.create_element("CSV.House", QtCore.QPointF(100, 80))
        self.model.set_param_value(house_1, 'datafile', os.path.normpath('maverig/tests/data/household_1_2.small.csv'))
        house_2 = self.model.create_element("CSV.House", QtCore.QPointF(100, 100))
        self.model.set_param_value(house_2, 'datafile', os.path.normpath('maverig/tests/data/household_1_4.small.csv'))

        assert self.model.param_is_multivalue([house_1, house_2], 'num_res') is True

        self.model.set_param_value(house_2, 'datafile', os.path.normpath('maverig/tests/data/household_1_2.small.csv'))

        assert self.model.param_is_multivalue([house_1, house_2], 'num_res') is False

    def test_docking_attrs(self):
        """Return a set of valid attribute connection tuples from one element to another."""
        refbus_1 = self.model.create_element("PyPower.RefBus", QtCore.QPointF(100, 80))
        bus_1 = self.model.create_element("PyPower.PQBus", QtCore.QPointF(100, 100))
        branch_1 = self.model.create_element("PyPower.Branch", QtCore.QPointF(100, 120))
        wecs_1 = self.model.create_element('CSV.WECS', QtCore.QPointF(100, 60))
        self.model.dock([branch_1, '0'], [refbus_1, '0'])
        self.model.dock([branch_1, '1'], [bus_1, '0'])

        for x in self.model.docking_attrs(branch_1, bus_1):
            assert x is None

        for x in self.model.docking_attrs(branch_1, refbus_1):
            assert x is None

        self.model.dock([wecs_1, '0'], [bus_1, '0'])

        for x in self.model.docking_attrs(wecs_1, bus_1):
            assert x is not None

    def test_handle_scenario_error(self):
        """Creates output and error events and selects elements in elem_ids for visual feedback of scenario errors."""
        elem_id = self.model.create_element("PyPower.RefBus", QtCore.QPointF(100, 80))

        class SimpleScenarioError(ScenarioError):
            title = 'Scenario Error'
            console_text = 'Console Text'
            text = 'Text'
            info_text = 'Info Text'
            elem_ids = [elem_id]

        e = SimpleScenarioError()

        def on_output(s):
            assert (s == 'Simulation stopped') or (s == 'Scenario Error: Console Text')

        def on_error(title, text, info_text, elem_ids):
            assert title == e.title
            assert text == e.text
            assert info_text == e.info_text
            assert elem_ids == e.elem_ids

        self.model.output_event += on_output
        self.model.error_event += on_error

        self.model.handle_scenario_error(e)
        assert self.model.selection == [elem_id]

    def test_validate_scenario(self):
        """Validates the scenario."""
        assert self.model.validate_scenario() is False

        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))

        assert self.model.validate_scenario() is True

    def test_get_shared_published_attrs(self):
        """Return a filtered list of published attribute names which are contained in each element of elem_ids."""
        self.model.scenario = config.read_json(dataHandler.get_normpath('maverig/tests/data/demo_sim.mvrg'))
        self.model.set_selected('CSV.House_1', True)
        self.model.set_selected('CSV.PV_1', True)
        elem_ids = ['CSV.House_1', 'CSV.PV_1']

        for i in self.model.get_shared_published_attrs(elem_ids):
            assert i is not None

        self.model.set_selected('PyPower.Transformer_1', True)
        self.model.set_selected('CSV.PV_1', False)
        elem_ids2 = ['CSV.House_1', 'PyPower.Transformer_1']

        for i in self.model.get_shared_published_attrs(elem_ids2):
            assert i is None
