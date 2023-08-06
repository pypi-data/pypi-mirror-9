import multiprocessing
import os
import sys
import datetime

from PySide import QtCore
import mosaik

from maverig.data import dataHandler
from maverig.utils.processServer import ServerProxy, ProcessServer
from maverig.utils.scenarioErrors import *
from maverig.data import config
import traceback


class SimulationProcess(multiprocessing.Process):
    def __init__(self, sim_proxy, model):
        "" ":type model: maverig.models.model.Model """
        super().__init__()
        self.sim_proxy = sim_proxy
        self.model = model
        self.elements = model.elements  # is an automatically pickled model elements copy passed into this process
        self.sim_start = str(model.sim_start)
        self.step_size = model.sim_step_size
        self.duration = model.duration
        self.name_extensions_enabled = True

    def run(self):
        """ process entry point """
        self.step_size = self.model.sim_step_size
        sys.stdout.write = self.sim_proxy.write
        self.step_size = self.model.sim_step_size
        try:
            self.start_simulation()
        except ScenarioError as e:
            self.sim_proxy.handle_process_scenario_error(e)

    def short_name(self, name):
        """ strip name extensions after '-' """
        if self.name_extensions_enabled:
            return name.split('-')[0]
        return name

    def start_simulation(self):
        """ start simulators and their elements in mosaik and create and run mosaik world  """
        sim_config = dict()
        # sim_config['WebVis'] = {'cmd': 'mosaik-web -s 0.0.0.0:8000 %(addr)s'}
        sim_config['VisSim'] = {'python': 'maverig.utils.visSimulator:VisSimulator'}

        # prepare dependent params
        for elem_id, elem in self.elements.items():
            comp = self.model.get_component(elem_id)
            sim = self.model.get_simulator(elem_id)

            sim_config[self.short_name(sim['name'])] = {sim['starter']: sim['address']}

            if comp.get('on_sim_init'):
                on_sim_init = config.import_method(comp['on_sim_init'])
                on_sim_init(self.model, elem)

            # expand relative filenames ('maverig/...') to full filenames
            for param_name, value in elem['params'].items():
                if isinstance(value, str) and os.path.isfile(dataHandler.get_normpath(value)):
                    elem['params'][param_name] = dataHandler.get_normpath(value)

            # fill simulator start-params with related element params
            elem['simulator'] = {
                'name': sim['name'],
                'params': {param_name: elem['params'].get(param_name, default_value)
                           for param_name, default_value in sim['params'].items()}
            }

            # set special global param sim_start
            if 'sim_start' in elem['params']:
                elem['params']['sim_start'] = self.sim_start
            if 'sim_start' in elem['simulator']['params']:
                elem['simulator']['params']['sim_start'] = self.sim_start

        # start simulators
        world = mosaik.World(sim_config)
        for elem in self.elements.values():
            if not elem.get('mosaik_simulator'):
                self.start_simulator(world, elem)

            self.start_element(elem)

        # item connections in mosaik
        for elem_id, elem in self.elements.items():
            for docking_port in elem['docking_ports'].values():
                for docked_id, _ in docking_port.get('out', []):
                    docked_elem = self.elements[docked_id]
                    if elem['mosaik_entity'].sid != docked_elem['mosaik_entity'].sid:
                        docking_attrs = self.model.docking_attrs(elem_id, docked_id)
                        world.connect(elem['mosaik_entity'], docked_elem['mosaik_entity'], *docking_attrs)

        # initialize visualization simulator
        vis_simulator = world.start('VisSim', start_date=self.sim_start, step_size=self.step_size,
                                    sim_proxy=self.sim_proxy, elements=self.elements)
        vis_topology = vis_simulator.Topology()
        for elem_id, elem in self.elements.items():
            comp_model = self.short_name(elem['sim_model'].split('.')[1])
            comp = self.model.get_component(elem_id)
            simmodel_attrs = elem['mosaik_simulator'].meta['models'][comp_model]['attrs']
            attrs = set(simmodel_attrs) & set(comp['attrs'])
            world.connect(elem['mosaik_entity'], vis_topology, *attrs)

        # initialize web visualization, open http://localhost:8000/
        # web_visualization = world.start('WebVis', start_date=self.sim_start, step_size=1000)
        # web_visualization.set_config(ignore_types=['Topology', 'ResidentialLoads', 'Grid', 'Database'])
        # web_visualization.set_etypes({
        # 'RefBus': {
        # 'cls': 'refbus',
        #         'attr': 'P',
        #         'unit': 'P [W]',
        #         'default': 0,
        #         'min': 0,
        #         'max': 30000,
        #     },
        #     'PQBus': {
        #         'cls': 'pqbus',
        #         'attr': 'Vm',
        #         'unit': 'U [V]',
        #         'default': 230,
        #         'min': 0.99 * 230,
        #         'max': 1.01 * 230,
        #     },
        #     'House': {
        #         'cls': 'load',
        #         'attr': 'P',
        #         'unit': 'P [W]',
        #         'default': 0,
        #         'min': 0,
        #         'max': 3000,
        #     },
        #     'PV': {
        #         'cls': 'gen',
        #         'attr': 'P',
        #         'unit': 'P [W]',
        #         'default': 0,
        #         'min': -10000,
        #         'max': 0,
        #     }
        # })
        #
        # web_topology = web_visualization.Topology()
        # for elem_id, elem in self.elements.items():
        #     comp = self.model.get_component(elem_id)
        #     if 'Bus' in comp['type']:
        #         world.connect(elem['mosaik_entity'], web_topology, 'P', 'Vm')
        #     elif not 'PowerTransmitter' in comp['type']:
        #         world.connect(elem['mosaik_entity'], web_topology, 'P')

        try:
            world.run(until=self.duration)
        except Exception as e:
            if isinstance(e, KeyError) and e.args[0] in ['I_imag', 'I_real']:
                branches = [elem_id for elem_id in self.elements if 'Branch' in self.model.get_component(elem_id)['type']]
                raise ScenarioSimulationPowerflowError(elem_ids=branches)
            else:
                raise ScenarioSimulationRuntimeError(tb=traceback.format_exc())

    def start_simulator(self, world, elem):
        """ starts a mosaik_simulator with elem.simulator.params """
        sim_name = elem['simulator']['name']
        try:
            # start simulator in mosaik
            elem['mosaik_simulator'] = world.start(self.short_name(sim_name), **elem['simulator']['params'])
        except FileNotFoundError as e:
            raise ScenarioFileNotFoundError(elem_id=elem['elem_id'], sim_name=sim_name, filename=e.filename)
        except:
            raise ScenarioSimulatorError(elem_id=elem['elem_id'], sim_name=sim_name, tb=traceback.format_exc())

        for other_elem in self.elements.values():
            if other_elem['simulator'] == elem['simulator']:
                other_elem['mosaik_simulator'] = elem['mosaik_simulator']

    def start_element(self, elem):
        """ create an element in mosaik with needed params specified in simulator meta and collected from elem.
        apply the mapping of mosaik_full_id (mosaik element id) to elem.
        """
        comp_model = self.short_name(elem['sim_model'].split('.')[1])
        comp_meta = elem['mosaik_simulator'].meta['models'].get(comp_model)

        if not comp_meta:
            raise ScenarioComponentError(elem_id=elem['elem_id'], sim_model=elem['sim_model'])
        if comp_meta['public']:
            # create element in mosaik
            elem_params = {param_name: elem['params'][param_name]
                           for param_name in comp_meta['params']
                           if param_name in elem['params']}

            try:
                # create element in mosaik
                comp_factory = getattr(elem['mosaik_simulator'], comp_model)
                entity = comp_factory(**elem_params)

                elem['mosaik_entity'] = entity
                elem['mosaik_full_id'] = entity.full_id
                self.sim_proxy.map_elem_to_mosaik(elem['elem_id'], elem['mosaik_full_id'])

                # set mosaik_full_id of child elements
                for child_entity in entity.children:
                    child_elem_id = child_entity.eid.split('-', 1)[-1]  # get right part after first '-' of eid
                    child_elem = self.elements[child_elem_id]
                    child_elem['mosaik_entity'] = child_entity
                    child_elem['mosaik_full_id'] = child_entity.full_id
                    self.sim_proxy.map_elem_to_mosaik(child_elem['elem_id'], child_elem['mosaik_full_id'])

            except:
                raise ScenarioElementError(elem_id=elem['elem_id'], tb=traceback.format_exc())

        elif not elem.get('mosaik_entity'):
            # create parent element in mosaik and assign mosaik_full_ids to child entities
            sim = self.model.get_simulator(elem['elem_id'])
            sim['on_sim_init_parents']

            if sim.get('on_sim_init_parents'):
                on_sim_init_parents = config.import_method(sim['on_sim_init_parents'])

                for parent_elem in on_sim_init_parents(self.model, elem):
                    parent_elem['mosaik_simulator'] = elem['mosaik_simulator']
                    self.start_element(parent_elem)


class SimulationServer(ProcessServer):
    """ manage a simulation process and serve proxy-access to registered functions """

    def __init__(self, model):
        """ :type model: maverig.models.model.Model """
        super().__init__()
        self.model = model
        self.process = None

        # define which functions can be accessed by proxy
        self.register_function('write')
        self.register_function('handle_process_scenario_error')
        self.register_function('map_elem_to_mosaik')
        self.register_function('update_data')

        # define how to start simulation process. Process params will get pickled (e.g. mini_model)
        mini_model = self.model.copy()
        self.register_process_factory(lambda: SimulationProcess(ServerProxy(self), mini_model))
        self.new_line = True

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_iteration)
        self.stamps = []
        self.progresses = []
        self.data = []
        self.iter = 0

    def start(self):
        """ reset attributes and start simulation process """
        self.process_factories.clear()
        mini_model = self.model.copy()
        self.register_process_factory(lambda: SimulationProcess(ServerProxy(self), mini_model))
        for elem_id, elem in self.model.elements.items():
            comp = self.model.get_component(elem_id)
            for attr_name in comp['attrs']:
                if comp['attrs'][attr_name].get('static'):
                    elem['attrs'][attr_name] = None
                else:
                    elem['attrs'][attr_name] = []
        super().start()

    def stop(self):
        super().stop()
        self.timer.stop()
        self.stamps = []
        self.progresses = []
        self.data = []
        self.iter = 0
        self.model.output_event('Simulation stopped')

    def write(self, text):
        if text == '\r':
            self.new_line = False
        elif text == '\n':
            self.new_line = True
        else:
            if self.new_line is True:
                self.model.output_event(text, new_line=self.new_line)

    def handle_process_scenario_error(self, e):
        self.model.handle_scenario_error(e)

    def map_elem_to_mosaik(self, elem_id, mosaik_full_id):
        elem = self.model.elements.get(elem_id)
        if elem:
            elem['mosaik_full_id'] = mosaik_full_id

    def update_data(self, timestamp, progress, data):
        self.data.append(data)
        if not self.timer.isActive():
            self.timer.start(100)
        self.stamps.append(self.model.sim_start + datetime.timedelta(0, timestamp))
        self.progresses.append(progress)

    def run_iteration(self):
        try:
            self.model.sim_timestamps.append(self.stamps[self.iter])
            self.model.sim_progress = (round(self.progresses[self.iter]))
            for elem_id, elem in self.model.elements.items():
                comp = self.model.get_component(elem_id)
                for attr_name in elem['attrs']:
                    value = self.data[self.iter][elem['mosaik_full_id']][attr_name]
                    if comp['attrs'][attr_name].get('static'):
                        elem['attrs'][attr_name] = value
                    else:
                        elem['attrs'][attr_name].append(value)
            self.model.output_event("Progress: " + str(self.progresses[self.iter])[:5] + "%", new_line=False)
            self.iter += 1
            self.model.update()

        # In fact, the simulation data from maverig gets in very fast at the end, so to programm will not
        # react. To prevent this, run_iteration and a timer deliver the information divided.
        # This causes IndexErrors, because not every percent of sim_progress is reviewed any longer.
        # Exp: Revieved percents are: 82, 86, 91, 93, 97, 101. Timer finishes when progress is 100,
        # so last seen percents would be 97. This case is seen and the progress will be rounded to 100.

        except IndexError:
            if self.model.sim_progress >= 100*((self.model.sim_end_index-1)/self.model.sim_end_index):
                self.model.sim_progress=100
                self.model.progress_event.demand()
                self.model.update()
            self.timer.stop()