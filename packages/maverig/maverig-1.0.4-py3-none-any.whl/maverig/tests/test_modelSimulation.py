from unittest import TestCase
from maverig.data import config, dataHandler
from maverig.models.modelSimulation import SimulationServer, SimulationProcess
from maverig.utils.processServer import ServerProxy, ProcessServer
from maverig.models.model import Model


class TestModelSimulation(TestCase):
    def setUp(self):
        self.model = Model()
        path = dataHandler.get_normpath('maverig/scenarios/demo.mvrg')
        self.model.scenario = config.read_json(path)
        self.simulation = SimulationServer(self.model)

    #    mini_model = self.model.copy()
    #    self.simulation_process = SimulationProcess(ServerProxy(self), mini_model)

    #def test_start(self):
    #    self.simulation.start()
    #
    #    assert len(self.simulation.stamps) > 0
    #
    #    self.simulation.stop()

    def test_stop(self):
        self.simulation.port = 5556
        self.simulation.start()
        self.simulation.stop()

        assert len(self.simulation.stamps) == 0

    def test_write(self):
        """ already tested in test_model.py """

    def test_handle_process_scenario_error(self):
        """ already tested in test_model.py """

    def test_map_elem_to_mosaik(self):
        """ todo """

    def test_update_data(self):
        """ todo """

    def test_run_iteration(self):
        self.simulation.port = 5557
        self.simulation.start()
        self.simulation.run_iteration()
        self.simulation.stop()

    #def test_run(self):
    #    self.simulation_process.start_simulation()