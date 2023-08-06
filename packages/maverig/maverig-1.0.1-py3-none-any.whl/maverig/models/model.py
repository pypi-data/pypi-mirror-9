import os
from datetime import datetime
import bisect
from dateutil import parser as dateparser

from maverig.data import config
from maverig.data import dataHandler
from maverig.utils import colorTools
from maverig.utils.event import Event
from maverig.utils.scenarioErrors import *
from maverig.models.modelSimulation import SimulationServer
from maverig.models.modelGraph import ModelGraph
from PySide.QtCore import QPointF
from collections import namedtuple
from numpy import ndarray


"""
########### Event Sequence: ###########
0. all Presenters that want to be informed about model mode changes set Event Listener:
   self.model.mode_event += self.on_mode

1. GUI click > Presenter1 > Presenter1 changes mode in model >
   Model > mode_event.demand() signalizes that there is a demand to inform Listeners that model has been changed

2. Presenter1 > Model: self.model.update() which fires all demanded Events to Listeners >

3. Model fires mode_event() > Presenter2 on_mode() > Presenter2 compares model state with gui and updates GUI buttons.
   Any Presenter (1,2...) may react on model changes and update GUI to actual model state
   This is especially important for the support of undo/redo and save/load where the complete Scenario might change.
   Hereby we can decide on our own, which model states (e.g. selection ) should be stored and loaded.


########### Element Example: ###########
Elements dictionaries represent a Power Unit (here a PQBus example) with customizable data for the following purposes:
- link to component description (sim_model) by model.get_component(elem_id) or model.components[sim_model]
  (here in maverig/data/components/bus.json)
- reference data (elem_id)
- custom visualization (icon),
- positioning for each port (pos),
- dockings to/from other elements and their ports (out, in),
- data for simulation runtime and initialization:
    - parameters and their values (params)
    - attributes at simulation runtime with their static or listed dynamic values (attrs)
    - reference to mosaik entity (mosaik_full_id)
      mosaik_full_id and attrs will be automatically filled during simulation time

Element dictionary for PyPower PQBus instance:
{
    "sim_model": "PyPower.PQBus",
    "icon": "bus.svg",
    "elem_id": "PyPower.PQBus_4",
    "mosaik_full_id": "PyPower-0.0-PyPower.PQBus_4",
    "docking_ports": {
        "0": {
            "pos": [450.0,200.0]
            "out": [],
            "in": [["PyPower.Branch_3","1"], ["PyPower.Branch_5","0"], ["CSV.House_4","1"]],
        }
    },
    "params": {
        "bus_type": "PQ",
        "base_kv": 0.23,
        "fbus": null,
        "tbus": null
    },
    "attrs": {
        "Vl": 230.0,
        "Q": [0.0, 0.0, 0.0],
        "Vm": [230.14789278916751, 230.23588331696217, 230.22035839218473],
        "P": [381.21, 174.35, 116.43999999999998],
        "Va": [-0.17130258343689386, -0.17013456872934510, -0.16981416413842957]
    }
}
"""


def fast_deepcopy(x):
    """Return a deepcopy of *x*.

    *x* may be or contain the following types::

        {dict, set, list, tuple, datetime, string, int, float, bool, NoneType}

    """
    # return copy.deepcopy(x)

    if isinstance(x, QPointF):
        return QPointF(x)

    if isinstance(x, (str, int, float, bool)) or x is None:
        result = x
        return result

    if isinstance(x, datetime):
        return datetime(x.year, x.month, x.day, x.hour, x.minute, x.second, x.microsecond, x.tzinfo)

    if isinstance(x, dict):
        return {fast_deepcopy(key): fast_deepcopy(value) for key, value in x.items()}

    if isinstance(x, set):
        return {fast_deepcopy(key) for key in x}

    if isinstance(x, list):
        return [fast_deepcopy(item) for item in x]

    if isinstance(x, tuple):
        return tuple([fast_deepcopy(item) for item in x])

    if isinstance(x, ndarray):
        # copy only reference for numpy arrays
        return x

    print('datatype %s not supported.' % str(type(x)))


ElemPort = namedtuple('ElemPort', 'elem_id, port')  # consist of internal model specific element id and port number
"""An element port instance (e.g. ``ElemPort('CSV.House_1', '0')``) describes a specific ``port`` (e.g. ``'0'``)
of an element specified by ``elem_id`` (e.g. ``'CSV.House_1'``), which may be docked to other element ports.

Element ports are often abbreviated with ``ep``.

In all model methods, element ports can also be passed as list (e.g. ``['CSV.House_1', '0']`` and will
be automatically converted to *ElemPort* when needed."""


class Mode:
    """Represents the currently selected mode for the composition."""
    selection = "selection mode"
    """In selection mode, all elements may be moved and edited."""

    hand = "hand mode"
    """In hand mode, the complete scenario is movable and elements can't be edited or created."""

    comp = "component mode"
    """In component mode, only elements of a the selected component in mode panel may be edited and created."""

    sim = "simulation mode"
    """In simulation mode, the scenario can only be watched and elements can't be edited.
    Similar to hand mode but may differ in element visualizations."""


class ProgramMode:
    """Represents the main program mode: composition, simulation, or simulation paused."""
    composition = "composition mode"
    """Composition mode, where scenario can be edited."""

    simulation = "simulation mode"
    """Simulation mode, where simulation or recorded simulation history "video" is running."""

    simulation_paused = "simulation paused"
    """Simulation paused mode, where simulation is paused."""


class Model():
    """Model manages the complete scenario state:
        - simulation start and end time
        - elements as component instances and their dockings
        - clipboard
        - selected elements
        - modi (comp_mode, selection_mode, hand_mode) and
        - events.
    """

    def __init__(self):
        """Initializes the model."""
        self.auto_update_components_languages = False
        """Switch for automatic creation of *.po language entries for new component texts."""

        self.history_undo = []
        """The history list of scenarios that can be undone.
        ``history_undo[-1]`` is the nearest to the current scenario."""

        self.history_redo = []
        """The history list of scenarios that can be redone.
        ``history_redo[-1]`` is the nearest to the current scenario."""

        self.tmp_scenario_copy = None
        """A copy of the current scenario since the last history relevant change occured."""

        self.saved_scenario_copy = None

        self.last_change_count = 0
        self.uid = dict()
        self.__sim_start = datetime(2014, 10, 20, 0, 0, 0)
        self.__sim_end = datetime(2014, 10, 24, 23, 59, 59)
        self.__sim_step_size = 1800  # seconds

        self.__sim_index = 0
        self.__sim_progress = 0
        self.__vid_speed = 1000
        self.__vid_speed_rel = 1
        self.sim_timestamps = []

        # self.__time_in_hours = self.__sim_start
        self.elements = dict()  # a dict mapping elem_id to element instance
        self.__components = dict()  # a dict mapping sim_model to component description
        self.__simulators = dict()  # a dict mapping sim_name to simulator description
        self.clipboard_elements = dict()
        self.__selection = []  # elem_ids
        self.__icon_colors = dict()

        self.__language = None
        self.__mode = Mode.selection
        self.__program_mode = ProgramMode.composition
        self.__comp = None
        self.__raster_mode = True
        self.__comp_raster = True
        self.__raster_snap_mode = True
        self.__force_dragging = False
        self.__selection_dragging = False
        self.__sim_mode = False

        # events fired by presenter on model changes
        self.settings_event = Event()
        self.components_event = Event()
        self.sim_event = Event()
        self.progress_event = Event()
        self.mode_event = Event()
        self.program_mode_event = Event()
        self.elements_event = Event()
        self.dockings_event = Event()
        self.drag_event = Event()
        self.positions_event = Event()
        self.selection_event = Event()
        self.param_event = Event()
        self.attrs_event = Event()
        self.clipboard_event = Event()
        self.language_event = Event()
        self.vid_speed_event = Event()
        self.test_event = Event()

        self.output_event = Event()  # param: string
        self.error_event = Event()  # params: title, text, info_text strings and elem_ids list

        self.__events_order = [self.settings_event, self.components_event, self.language_event,
                               self.elements_event, self.dockings_event, self.positions_event,
                               self.selection_event, self.param_event, self.clipboard_event,
                               self.mode_event, self.program_mode_event, self.drag_event,
                               self.sim_event, self.progress_event, self.attrs_event, self.vid_speed_event,
                               self.test_event]

        # events that are considered as model state changers for history
        self.__history_specific_events = [self.sim_event, self.elements_event, self.dockings_event,
                                          self.positions_event, self.param_event]

        self.__simulation = None
        self.__graph = None

        self.init_history()

    @property
    def graph(self):
        """Return the graph of the created scenario."""
        if not self.__graph:
            self.__graph = ModelGraph(self)
        return self.__graph

    @property
    def simulation(self):
        """Sets the SimulationsServer."""
        if not self.__simulation:
            self.__simulation = SimulationServer(self)
        return self.__simulation

    @property
    def components(self):
        """Return the JSON-Files of the components in the scenario."""
        if not self.__components:
            self.__components = config.read_components()
        return self.__components

    @components.setter
    def components(self, value):
        if self.__components != value:
            self.__components = value
            if self.auto_update_components_languages:
                config.create_components_language_po_entries(self.__components)
            self.components_event.demand()

    @property
    def simulators(self):
        """Return the simulator of an element."""
        if not self.__simulators:
            self.__simulators = config.read_simulators()
        return self.__simulators

    @simulators.setter
    def simulators(self, value):
        """Sets the simulator of an element."""
        self.__simulators = value

    def __reset_simulation_data(self):
        """Resets the simulation data to timestamp zero."""
        self.sim_timestamps.clear()
        self.__sim_index = 0
        self.__sim_progress = 0

    @property
    def sim_start(self):
        """Return the simulation start time."""
        return self.__sim_start

    @sim_start.setter
    def sim_start(self, value):
        """Sets the simulation start time to a specific time."""
        if self.__sim_start != value:
            self.__sim_start = value
            self.sim_event.demand()

    @property
    def sim_end(self):
        """Return the simulation end time. """
        return self.__sim_end

    @sim_end.setter
    def sim_end(self, value):
        """Sets the simulation end time to an specific time."""
        if self.__sim_end != value:
            self.__sim_end = value
            self.sim_event.demand()

    @property
    def sim_step_size(self):
        """Return the step size of the simulation."""
        return self.__sim_step_size

    @sim_step_size.setter
    def sim_step_size(self, value):
        """Sets the step size of the simulation to a specific step."""
        if self.__sim_step_size != value:
            self.__sim_step_size = value
            self.sim_event.demand()

    @property
    def sim_index(self):
        """Return the current simulation time index."""
        return self.__sim_index

    @sim_index.setter
    def sim_index(self, value):
        """Set the current simulation time index to the closest valid index from value."""
        value = min(value, len(self.sim_timestamps) - 1)
        if self.__sim_index != value:
            self.__sim_index = value
            self.sim_event.demand()
            self.attrs_event.demand()

    @property
    def sim_end_index(self):
        """ Return the last possible simulation time index."""
        return int(self.duration / self.sim_step_size)

    @property
    def vid_speed(self):
        """Return the current speed of the shown simulation."""
        return self.__vid_speed

    @vid_speed.setter
    def vid_speed(self, value):
        """Sets the speed of the shown simulation."""
        if self.__vid_speed != value:
            self.__vid_speed = value
            self.vid_speed_event.demand()

    @property
    def vid_speed_rel(self):
        return self.__vid_speed_rel

    @vid_speed_rel.setter
    def vid_speed_rel(self, value):
        if self.__vid_speed_rel != value:
            self.__vid_speed_rel = value
            self.vid_speed_event.demand()

    @property
    def sim_progress(self):
        """Return the progress of the simulation."""
        return self.__sim_progress

    @sim_progress.setter
    def sim_progress(self, value):
        """Sets the progress of the simulation."""
        if self.__sim_progress != value:
            self.__sim_progress = value
            self.progress_event.demand()

    @property
    def sim_timestamp(self):
        """Return the time stamps of the current simulation time index."""
        if self.sim_timestamps:
            return self.sim_timestamps[self.sim_index]
        else:
            return self.sim_start

    @sim_timestamp.setter
    def sim_timestamp(self, value):
        """Set the current simulation timestamp which is previous or equal to value."""
        self.sim_index = max(bisect.bisect(self.sim_timestamps, value) - 1, 0)

    @property
    def duration(self):
        """Return the simulation duration in seconds."""
        return round((self.sim_end - self.sim_start).total_seconds())

    @property
    def language(self):
        """Return the currently installed language for internationalization (e.g. 'en_EN')."""
        return self.__language

    @language.setter
    def language(self, value):
        """Set the currently installed language for internationalization (e.g. 'en_EN')."""
        if self.__language != value:
            self.__language = value
            self.language_event.demand()

    @property
    def mode(self):
        """Return the current mode."""
        return self.__mode

    @mode.setter
    def mode(self, value):
        """Sets the current mode to another mode."""
        if self.__mode != value:
            self.__mode = value
            self.mode_event.demand()

    @property
    def program_mode(self):
        """Return the current mode in the simulation (play, paused, composition)."""
        return self.__program_mode

    @program_mode.setter
    def program_mode(self, value):
        """Sets the current program_mode (play, paused, composition)."""
        if self.__program_mode != value:
            if value == ProgramMode.composition:
                self.__reset_simulation_data()
            self.__program_mode = value
            self.program_mode_event.demand()

    def switch_modes(self, standard_mode, substitute_mode):
        """Switch current mode between given standard and substitute mode.
        If current mode is none of these, it will be set to standard mode."""
        self.mode = substitute_mode if self.mode == standard_mode else standard_mode
        self.mode_event.demand()

    @property
    def comp(self):
        """Return the current component."""
        return self.__comp

    @comp.setter
    def comp(self, value):
        """Set the current component for components mode."""
        if self.__comp != value:
            self.__comp = value
            self.mode_event.demand()

    @property
    def raster_mode(self):
        """Return whether raster is shown or not."""
        return self.__raster_mode

    @raster_mode.setter
    def raster_mode(self, value):
        """Sets whether raster is shown or not."""
        if self.__raster_mode != value:
            self.__raster_mode = value
            self.mode_event.demand()

    @property
    def comp_raster(self):
        """Return whether raster is shown or not."""
        return self.__comp_raster

    @comp_raster.setter
    def comp_raster(self, value):
        """Sets whether raster is shown or not."""
        if self.__comp_raster != value:
            self.__comp_raster = value
            self.mode_event.demand()

    @property
    def raster_snap_mode(self):
        """Return whether elements snap to raster positions on mouse_release."""
        return self.__raster_snap_mode

    @raster_snap_mode.setter
    def raster_snap_mode(self, value):
        """Sets whether elements snap to raster positions on mouse_release."""
        if self.__raster_snap_mode != value:
            self.__raster_snap_mode = value
            self.mode_event.demand()

    @property
    def force_dragging(self):
        """
        :return:?
        """
        return self.__force_dragging

    @force_dragging.setter
    def force_dragging(self, value):
        """
        :return:?
        """
        if self.__force_dragging != value:
            self.__force_dragging = value
            self.drag_event.demand()

    @property
    def selection_dragging(self):
        """
        :return:?
        """
        return self.__selection_dragging

    @selection_dragging.setter
    def selection_dragging(self, value):
        """
        :return:?
        """
        if self.__selection_dragging != value:
            self.__selection_dragging = value
            self.drag_event.demand()

    @property
    def selection(self):
        """Return the selected elements."""
        return self.__selection

    @selection.setter
    def selection(self, value):
        """Sets an element as selected."""
        current_set = set(self.__selection)
        value_set = set(value)
        if current_set != value_set:
            # preserve order
            preserved_elem_ids = [e for e in self.__selection if e in value_set]
            new_elem_ids = [e for e in value if e not in current_set and e in self.elements]
            self.__selection = preserved_elem_ids + new_elem_ids
            self.selection_event.demand()

    def is_selectable(self, elem_or_elem_id):
        """Return whether element is selectable according to mode."""
        if elem_or_elem_id is None:
            return False
        if isinstance(elem_or_elem_id, dict):
            elem = elem_or_elem_id
        else:
            elem_id = elem_or_elem_id
            elem = self.elements[elem_id]
        return self.mode in (Mode.selection, Mode.sim) or (self.mode == Mode.comp and self.comp == elem['sim_model'])

    def init_history(self):
        """Initial history entry for first scenario state."""
        self.history_undo = []
        self.tmp_scenario_copy = self.saved_scenario_copy = fast_deepcopy(self.scenario)
        self.history_redo = []

        self.last_change_count = self.changes_count()

    def add_history_point(self):
        """Adds a new history point if there have been some changes and clears redo history list."""
        has_changes = self.changes_count() != self.last_change_count

        if has_changes:
            self.history_undo.append(self.tmp_scenario_copy)
            self.tmp_scenario_copy = fast_deepcopy(self.scenario)
            self.history_redo = []
            self.last_change_count = self.changes_count()

    def undo(self):
        """Undo latest change."""
        if self.history_undo:
            self.history_redo.append(self.tmp_scenario_copy)
            self.tmp_scenario_copy = self.history_undo.pop()
            self.scenario = fast_deepcopy(self.tmp_scenario_copy)

    def redo(self):
        """Redo latest undone change."""
        if self.history_redo:
            self.history_undo.append(self.tmp_scenario_copy)
            self.tmp_scenario_copy = self.history_redo.pop()
            self.scenario = fast_deepcopy(self.tmp_scenario_copy)

    def changes_count(self):
        """Return an int value representing the current model state changes counter."""
        return sum([event.demands_count for event in self.__history_specific_events])

    @property
    def scenario(self):
        """Return a scenario dict."""
        return {
            'uid': self.uid,
            'sim_start': self.sim_start.isoformat(),
            'sim_end': self.sim_end.isoformat(),
            'sim_step_size': self.sim_step_size,
            'elements': self.elements,
            'selection': self.selection
        }

    @scenario.setter
    def scenario(self, value):
        """Apply a scenario dict to model."""
        self.uid = value['uid']
        self.sim_start = dateparser.parse(value['sim_start'])
        self.sim_end = dateparser.parse(value['sim_end'])
        self.sim_step_size = value['sim_step_size']
        self.elements = value['elements']
        self.selection = value['selection']
        self.update_all()

    def copy(self):
        """Return a new flat copied model including...
        - scenario
        - components and simulators descriptions
        - no connected events."""
        new_model = Model()
        new_model.auto_update_components_languages = False
        new_model.scenario = self.scenario
        new_model.components = self.components
        new_model.simulators = self.simulators
        return new_model

    def __new_elem_id(self, sim_model):
        """Create an element id for a new element."""
        self.uid.setdefault(sim_model, 0)
        self.uid[sim_model] += 1
        return sim_model + "_" + str(self.uid[sim_model])

    def copy_to_clipboard(self, elem_ids):
        """Copies all elements of the elem_ids list to an internal clipboard."""
        # empty clipboard
        self.clipboard_elements = {}

        # copy elements
        for elem_id in elem_ids:
            self.clipboard_elements[elem_id] = fast_deepcopy(self.elements[elem_id])

        self.clipboard_event.demand()

    def paste_from_clipboard(self):
        """Paste all elements from internal clipboard and return the new elem_ids
        only dockings inside of clipboard will be maintained."""
        # clone clipboard and set new ids (keys are still old_ids)
        old2new_paste_elements = fast_deepcopy(self.clipboard_elements)
        paste_elements = old2new_paste_elements.values()
        for elem in paste_elements:
            elem['elem_id'] = self.__new_elem_id(elem['sim_model'])

        def get_new_id(old_id):
            if old_id in old2new_paste_elements:
                return old2new_paste_elements[old_id]['elem_id']
            return None

        def new_dockings(old_dockings):
            """Renew id's in element dockings and forget those that are out of scope."""
            result = []
            for old_id, port in old_dockings:
                new_id = get_new_id(old_id)
                if new_id:
                    result.append([new_id, port])
                    self.dockings_event.demand()
            return result

        # maintain available dockings inside of paste-elements-dict and set the new reference id's
        for elem in paste_elements:
            for p in elem['docking_ports'].values():
                p['out'] = new_dockings(p['out'])
                p['in'] = new_dockings(p['in'])

        # paste
        for elem in paste_elements:
            self.elements[elem['elem_id']] = elem
            self.elements_event.demand()

        return [elem['elem_id'] for elem in paste_elements]

    def create_element(self, sim_model, pos):
        """Creates a new element with a specific sim_model on an specific position in scenario."""
        comp = self.components[sim_model]

        elem_id = self.__new_elem_id(sim_model)
        self.elements[elem_id] = {
            'elem_id': elem_id,
            'sim_model': sim_model,
            'icon': comp['icon'],
            'params': {param_name: param.get('default_value')
                       for param_name, param in comp['params'].items()},
            'attrs': {},  # attributes will be filled during simulation
            'docking_ports': {port: {'pos': pos.toTuple(), 'in': [], 'out': []}
                              for port in comp['docking_ports']}
        }

        self.elements_event.demand()
        return elem_id

    def delete_element(self, elem_id):
        """Delete the given element."""
        elem = self.elements[elem_id]

        # remove dockings
        for port, data in elem['docking_ports'].items():
            ep = ElemPort(elem_id, port)
            for to_ep in data['out'].copy():
                self.undock(ep, ElemPort(*to_ep))

            for from_ep in data['in'].copy():
                self.undock(ElemPort(*from_ep), ep)

        # remove elem_id from
        if elem_id in self.selection:
            self.selection.remove(elem_id)
            self.selection_event.demand()

        # remove element elem_id
        del self.elements[elem_id]
        self.elements_event.demand()

    def get_component(self, elem_id):
        """Return the componenet of an elem_id."""
        elem = self.elements[elem_id]
        try:
            return self.components[elem['sim_model']]
        except KeyError:
            print('Component is not existing.')

    def get_simulator(self, elem_id):
        """Return the simulator from an element."""
        elem = self.elements[elem_id]
        sim_name = elem['sim_model'].split('.')[0]
        return self.simulators[sim_name]

    def get_icon_color(self, elem_id):
        """Return the color of the element icon."""
        elem = self.elements[elem_id]
        icon = elem['icon']
        if not icon in self.__icon_colors:
            self.__icon_colors[icon] = colorTools.get_icon_color(dataHandler.get_component_icon(icon))
        return self.__icon_colors[icon]

    def get_shared_published_params(self, elem_ids):
        """Return a filtered list of published parameter names which are contained in each element of elem_ids."""
        if not elem_ids:
            return []
        comp = self.get_component(elem_ids[0])
        is_shared = lambda param_name: all([param_name in self.elements[elem_id]['params']
                                            for elem_id in elem_ids])
        return filter(is_shared, comp['published_params'])

    def param_is_multivalue(self, elem_ids, param_name):
        """Return whether parmeter values differ in elements of elem_ids."""
        return len({str(self.elements[elem_id]['params'][param_name]) for elem_id in elem_ids}) > 1

    def get_param_value(self, elem_id, param_name):
        """Get value of parameter with param_name in element elem_id,
           return None if param_name does not exist."""
        elem = self.elements[elem_id]
        return elem['params'].get(param_name)

    def set_param_value(self, elem_id, param_name, param_value):
        """Set value of parameter with param_name in element elem_id if value is not None."""
        elem = self.elements[elem_id]

        ignore_param = param_value is None
        if elem['params'][param_name] != param_value and not ignore_param:
            elem['params'][param_name] = param_value

            comp = self.components[elem['sim_model']]
            if comp.get('on_set_param'):  # e.g. 'maverig.data.components.utils.simInit:on_set_param_house'
                on_set_param = config.import_method(comp['on_set_param'])
                on_set_param(self, elem, param_name)

            self.param_event.demand()

    def get_shared_published_attrs(self, elem_ids):
        """Return a filtered list of published attribute names which are contained in each element of elem_ids."""
        if not elem_ids:
            return []
        comp = self.get_component(elem_ids[0])
        is_shared = lambda attr_name: all([attr_name in self.elements[elem_id].get('attrs', {})
                                           for elem_id in elem_ids])
        return filter(is_shared, comp['published_attrs'])

    def attr_is_multivalue(self, elem_ids, attr_name):
        """Return whether current attribute values differ in elements of elem_ids."""
        return len({str(self.get_attr_value(elem_id, attr_name)) for elem_id in elem_ids}) > 1

    def get_attr_values(self, elem_id, attr_name, from_time_index=0, to_time_index=None):
        """Get attribute values of attr_name in element elem_id
        in time interval [from_time_index, to_time_index] where to_time_index is current timestamp if set to None."""
        if to_time_index is None:
            to_time_index = self.sim_index

        elem = self.elements[elem_id]
        comp = self.components[elem['sim_model']]

        values = elem.get('attrs', {}).get(attr_name)
        if values and not comp['attrs'][attr_name]['static']:
            return values[from_time_index:to_time_index + 1]
        else:
            return values

    def get_attr_value(self, elem_id, attr_name, time_index=None):
        """Get current attribute value of attr_name in element elem_id at current timestamp,
        return None if attr_name or value at current timestamp does not exist."""
        if time_index is None:
            time_index = self.sim_index

        elem = self.elements[elem_id]
        comp = self.components[elem['sim_model']]

        values = elem.get('attrs', {}).get(attr_name)
        if values and not comp['attrs'][attr_name]['static']:
            return values[time_index]
        else:
            return values

    def get_u_heat_value(self, elem_id):
        """Return the u_heat_value of an element with component type PQBus or Branch"""
        elem = self.elements[elem_id]
        comp = self.get_component(elem_id)
        if 'PQBus' in comp['type']:
            "return % to u_level"
            "when u_magnitude(real_value) is bigger than u_level(set current level) return negative %"
            "when u_magnitude(real_value) is smaller than u_level(set current level) return positive %"
            u_magnitude = self.get_attr_value(elem_id, 'Vm')
            u_level = self.get_attr_value(elem_id, 'Vl')

            u_heat_level = u_magnitude / u_level

            # return negative u_heat_level when u_heat_level is over 100%
            if u_heat_level > 1:
                u_heat_level = (u_heat_level - 1) * (-1)
            else:
                u_heat_level -= 1

            return u_heat_level

        elif 'Branch' in comp['type']:
            "return % to u_level"
            "when u_magnitude(real_value) is bigger than u_level(set current level) return negative %"
            "when u_magnitude(real_value) is smaller than u_level(set current level) return positive %"
            online = self.get_attr_value(elem_id, 'online')

            bus_elem_id, _ = elem['docking_ports']['0']['out'][0]  # get docked bus on port 0
            u_level = self.get_attr_value(bus_elem_id, 'Vl')

            if online:
                port_0, _ = elem['docking_ports']['0']['out'][0]  # get docked bus on port 0
                port_1, _ = elem['docking_ports']['1']['out'][0]  # get docked bus on port 1
                u_magnitude_port_0 = self.get_attr_value(port_0, 'Vm')
                u_magnitude_port_1 = self.get_attr_value(port_1, 'Vm')


                # Fehlerbehandlung i_max bzw. i_real error
                max = u_level * 1.15
                min = u_level - (u_level * 0.15)

                if (abs(u_magnitude_port_0) > max) \
                        or (abs(u_magnitude_port_0) < min) \
                        or (abs(u_magnitude_port_1) > max) \
                        or (abs(u_magnitude_port_1) < min):
                    self.handle_scenario_error(ScenarioSimulationBranchLengthError(elem_id))
                # --------------------------------------------

                # return negative u_heat_level when u_heat_level is over 100%
                if not (u_magnitude_port_0 >= u_level and u_magnitude_port_1 >= u_level):
                    voltage_drop = u_magnitude_port_0 - u_magnitude_port_1

                    if voltage_drop < 0:
                        voltage_drop *= -1
                        u_heat_level = voltage_drop / u_level
                    else:
                        u_heat_level = voltage_drop / u_level

                # return negative u_heat_level when u_heat_level is over 100%
                else:
                    if u_magnitude_port_0 >= u_magnitude_port_1:
                        u_heat_level = u_magnitude_port_0 / u_level
                        u_heat_level = (u_heat_level - 1) * (-1)
                    else:
                        u_heat_level = u_magnitude_port_1 / u_level
                        u_heat_level = (u_heat_level - 1) * (-1)

            return u_heat_level

        return None

    def get_i_heat_value(self, elem_id):
        """Return the i_heat_value of an element only with component type Branch"""
        elem = self.elements[elem_id]
        comp = self.get_component(elem_id)
        if 'Branch' in comp['type']:
            online = self.get_attr_value(elem_id, 'online')

            if online:
                i_real = self.get_attr_value(elem_id, 'I_real')
                i_imag = self.get_attr_value(elem_id, 'I_imag')
                i_max = self.get_attr_value(elem_id, 'I_max')

                i_heat_level = (i_real - i_imag) / i_max

                return i_heat_level
        return 0

    def get_p_level(self, elem_id):
        """Return the p_level of an element with component type House, PV, Transformer, CHP, WECS or EV."""
        elem = self.elements[elem_id]
        comp = self.get_component(elem_id)
        "return % to max level"
        "return % over 100 when p_real is bigger than max value"

        if 'House' in comp['type']:
            p_real = self.get_attr_value(elem_id, 'P')
            p_max = self.get_param_value(elem_id, 'P_max')

            p_level = p_real / p_max

            return p_level

        elif 'PV' in comp['type']:
            "return % to max level"
            "return % over 100 when p_real is bigger than max value"
            p_real = self.get_attr_value(elem_id, 'P')
            p_max = self.get_attr_value(elem_id, 'kw_peak')
            p_max *= 1000

            p_level = (p_real / p_max)
            # p_level = (p_real / p_max) * (-1)

            return p_level

        elif 'Transformer' in comp['type']:
            "return % to max level"
            "return % over 100 when p_real is bigger than max value"

            i_max_primary = self.get_attr_value(elem_id, 'I_max_p')
            i_max_secondary = self.get_attr_value(elem_id, 'I_max_s')

            u_primary = self.get_attr_value(elem_id, 'U_p')
            u_secondary = self.get_attr_value(elem_id, 'U_s')

            p_max_primary = i_max_primary * u_primary
            p_max_secondary = i_max_secondary * u_secondary

            p_from = abs(self.get_attr_value(elem_id, 'P_from'))
            p_to = abs(self.get_attr_value(elem_id, 'P_to'))

            p_level_primary = p_from / p_max_primary
            p_level_secondary = p_to / p_max_secondary

            return p_level_primary, p_level_secondary

        elif 'CHP' in comp['type']:
            p_real = self.get_attr_value(elem_id, 'P')
            p_max = self.get_attr_value(elem_id, 'P_max')
            p_max *= 1000

            # TODO: Implement min max values
            p_level = (p_real / p_max)
            # p_level = (p_real / p_max) * (-1)

            return p_level

        elif 'WECS' in comp['type']:
            " % to max level"
            "return % over 100 when p_real is bigger than max value"

            p_real = self.get_attr_value(elem_id, 'P')
            p_max = self.get_attr_value(elem_id, 'P_max')
            p_max *= 1000

            # TODO: Implement min max values
            p_level = (p_real / p_max)
            # p_level = (p_real / p_max) *(-1)

            return p_level

        elif 'EV' in comp['type']:
            "return % to max level"
            "return % over 100 when p_real is bigger than max value"
            p_real = self.get_attr_value(elem_id, 'P')
            p_max = self.get_attr_value(elem_id, 'P_crg')
            p_max *= 1000

            p_level = (p_real / p_max)

            # TODO: Implement min max values

            return p_level

        return 0

    def get_state_of_charge(self, elem_id):
        """Return the state of charge of an EV."""
        elem = self.elements[elem_id]
        comp = self.get_component(elem_id)

        "return % of State of Charge (SoC)"
        if 'EV' in comp['type']:
            soc = self.get_attr_value(elem_id, 'SoC')
            soc /= 100

            # TODO: Implement min max values

            return soc
        else:
            return None

    def get_selected(self, elem_id):
        """Get all selected elements."""
        return elem_id in self.selection

    def set_selected(self, elem_id, value):
        """Set an element as selected or deselected."""
        has_changed = value != self.get_selected(elem_id)

        if has_changed:
            if value:
                self.selection.append(elem_id)
            else:
                self.selection.remove(elem_id)
            self.selection_event.demand()
        return has_changed

    def docking_port(self, ep):
        """Return all dockings from a docking port."""
        ep = ElemPort(*ep)
        elem = self.elements.get(ep.elem_id)
        if elem:
            return elem['docking_ports'][ep.port]
        return None

    def elem_ports(self, elem_id):
        """Return the element ports."""
        elem = self.elements[elem_id]
        return [ElemPort(elem_id, port) for port in sorted(elem['docking_ports'])]

    def get_pos(self, ep):
        """Get the position of an element port."""
        return QPointF(*self.docking_port(ep)['pos'])

    def set_pos(self, ep, pos):
        """Set a position of an element port."""
        ep = ElemPort(*ep)
        self.docking_port(ep)['pos'] = pos.toTuple()
        self.graph.set_pos(ep, pos)
        self.positions_event.demand()

    def dockings_out(self, ep):
        """Return an array of outgoing element ports."""
        docking_port = self.docking_port(ep)
        if not docking_port:
            return []
        return [ElemPort(*to_ep) for to_ep in docking_port['out']]

    def dockings_in(self, ep):
        """Return an array of ingoing element ports."""
        docking_port = self.docking_port(ep)
        if not docking_port:
            return []
        return [ElemPort(*to_ep) for to_ep in docking_port['in']]

    def docking_attrs(self, from_elem_id, to_elem_id):
        """Return a set of valid attribute connection tuples from one element to another, e.g. {('P_out','P')}
        component attribute descriptions may contain 'out':[...] or 'in':[...] entries
        indicating allowed connections to or from other attribute names."""
        docking_attrs = set()
        from_comp = self.get_component(from_elem_id)
        to_comp = self.get_component(to_elem_id)
        for from_attr_name, from_attr in from_comp['attrs'].items():
            if from_attr_name in to_comp['attrs']:
                # connect equal attribute names
                docking_attrs.add((from_attr_name, from_attr_name))
            else:
                # connect to attributes matching with 'out'-list in from_comp['attrs'][attr_name]
                to_attr_names = set(from_attr.get('out', [])) & set(to_comp['attrs'])
                for to_attr_name in to_attr_names:
                    docking_attrs.add((from_attr_name, to_attr_name))

        for to_attr_name, to_attr in to_comp['attrs'].items():
            # connect from attributes matching with 'in'-list in to_comp['attrs'][attr_name]
            from_attr_names = set(from_comp['attrs']) & set(to_attr.get('in', []))
            for from_attr_name in from_attr_names:
                if to_attr_name == 'connect':
                    # special attribute "connect" signalizes which attributes may be collected
                    docking_attrs.add((from_attr_name, from_attr_name))
                else:
                    docking_attrs.add((from_attr_name, to_attr_name))
        return docking_attrs

    def can_dock(self, from_ep, to_ep):
        """Check whether it is possible to dock from one port to another."""
        from_ep = ElemPort(*from_ep)
        to_ep = ElemPort(*to_ep)
        from_comp = self.get_component(from_ep.elem_id)
        to_comp = self.get_component(to_ep.elem_id)

        from_accepted_out_types = from_comp['docking_ports'][from_ep.port].get('out', [])
        to_accepted_in_types = to_comp['docking_ports'][to_ep.port].get('in', [])

        can_dock_from = bool(set(from_accepted_out_types) & set(to_comp['type']))
        can_dock_to = bool(set(to_accepted_in_types) & set(from_comp['type']))

        def line_overlap():
            """ return whether docking would cause overlapping with other lines:
                other_lines_in --> (node_1) <----- line -----> (node_2) <-- other_lines_in """
            if 'line' in from_comp['drawing_mode']:
                from_ep2 = ElemPort(from_ep.elem_id, "0" if from_ep.port == "1" else "1")

                connected_nodes = [to_ep] + self.dockings_out(from_ep2)  # [node_1, node_2]
                shared_lines = set()
                # see, which lines are going into the first and second node and whether they share some
                for node in connected_nodes:
                    other_lines_in = {ep.elem_id for ep in self.dockings_in(node)} - {from_ep.elem_id}
                    # check whether some lines are already connected to the other node
                    if other_lines_in & shared_lines:  # intersection
                        return True
                    shared_lines |= other_lines_in
            return False

        return can_dock_from and can_dock_to and not line_overlap()

    def dock(self, from_ep, to_ep):
        """Dock one port to another port."""
        from_docking_port = self.docking_port(from_ep)
        to_docking_port = self.docking_port(to_ep)
        if not ElemPort(*to_ep).elem_id in [e for e, _ in from_docking_port['out']]:
            from_docking_port['out'].append(list(to_ep))
            to_docking_port['in'].append(list(from_ep))
            self.dockings_event.demand()

    def undock(self, from_ep, to_ep):
        """Undock two element ports. Only undock if element exists - undock might be caused by element deletion"""
        from_docking_port = self.docking_port(from_ep)
        if from_docking_port and list(to_ep) in from_docking_port['out']:
            from_docking_port['out'].remove(list(to_ep))
            self.dockings_event.demand()

        to_docking_port = self.docking_port(to_ep)
        if to_docking_port and list(from_ep) in to_docking_port['in']:
            to_docking_port['in'].remove(list(from_ep))
            self.dockings_event.demand()

    def handle_scenario_error(self, e):
        """Creates output and error events and selects elements in elem_ids for visual feedback of scenario errors."""
        self.stop_simulation()
        self.selection = e.elem_ids
        self.update()
        self.output_event('%s: %s' % (e.title, e.console_text))
        self.error_event(e.title, e.text, e.info_text, e.elem_ids)

    def validate_scenario(self):
        """Validates the scenario."""
        try:
            ref_bus_list = []

            if not self.elements:
                raise ScenarioEmptyError()

            for elem_id, elem in self.elements.items():
                comp = self.get_component(elem_id)

                if self.get_param_value(elem_id, 'online') is False:
                    raise ScenarioOfflineElementError(elem_id)

                if 'CSV' in comp['type']:
                    datafile = self.get_param_value(elem_id, 'datafile')
                    if not os.path.isfile(dataHandler.get_normpath(datafile)):
                        raise ScenarioDatafileError(elem_id)

                if 'PowerTransmitter' in comp['type']:
                    for docking_port in elem['docking_ports'].values():
                        if len(docking_port['out']) == 0:
                            raise ScenarioConnectionError(elem_id)

                        is_ref_bus = 'RefBus' in docking_port['out'][0][0]
                        if is_ref_bus:
                            ref_id = docking_port['out'][0][0]
                            ref_base_kv = self.get_param_value(ref_id, 'base_kv')
                            bus_id = ''
                            bus_base_kv = 0
                            for docking_port2 in elem['docking_ports'].values():
                                is_bus = 'PQBus' in docking_port2['out'][0][0]
                                if is_bus:
                                    bus_id = docking_port2['out'][0][0]
                                    bus_base_kv = self.get_param_value(bus_id, 'base_kv')
                            if ref_base_kv != bus_base_kv:
                                raise ScenarioBaseVoltageLevelError(ref_id, bus_id)

                if 'RefBus' in comp['type']:
                    ref_bus_list.append(elem_id)
                    for port in elem['docking_ports'].values():
                        if len(port['in']) != 1:
                            raise ScenarioRefBusConnectionError(elem_id)

            if len(ref_bus_list) == 0:
                raise ScenarioRefBusMissingError()

            if len(ref_bus_list) > 1:
                raise ScenarioRefBusCountError(ref_bus_list)

        except ScenarioError as e:
            self.handle_scenario_error(e)
            return False
        return True

    def update(self):
        """Fires all events with pending demands."""
        for event in self.__events_order:
            if event.demanded:
                event()

    def update_all(self):
        """Fires all events."""
        for event in self.__events_order:
            event()

    def deselect_all_elems(self):
        """Deselect all selected elements."""
        self.selection.clear()

    def stop_simulation(self):
        """Stop the simulation and switch the mode to selection and program_mode to composition."""
        self.simulation.stop()
        self.program_mode = ProgramMode.composition
        self.mode = Mode.selection
        self.update()