import json

from maverig.data import dataHandler


"""
This module is used for serializing created elements to a JSON formatted object. The JSON formatted object is needed
by the PyPower simulator to instantiate the elements for the simulation.

See `PyPower repository <https://bitbucket.org/mosaik/mosaik-pypower>`_ for more information. There is also an
`example <https://bitbucket.org/mosaik/mosaik-pypower/src/default/tests/data/test_case_b.json>`_ available.
"""


class PyPowerSerializer():
    """Util class that is used for serialization of the created elements which are depending on the PyPower simulator.
    Currently refBus, bus, transformer and branch belong to this group of elements."""

    __PP_JSON_FILE = 'pypower.json'

    def __init__(self):
        """Initialize the PyPowerSerializer holding the pre-formatted JSON object."""
        self.pp_json_object = {
            "bus": [],
            "trafo": [],
            "branch": []
        }

    def serialize(self, elements):
        """Serialize elements to a JSON formatted object.
        :param elements: dict of elements.
        :return: Serialized JSON formatted object.
        """
        self.__build_json(elements)

        return json.dumps(self.pp_json_object, indent=4)

    def serialize_to_file(self, elements):
        """Serialize elements as a JSON formatted stream to a file (.json).
        :param elements: dict of elements.
        :return: Path of the JSON file.
        """
        self.__build_json(elements)

        with open(dataHandler.get_temp_file(self.__PP_JSON_FILE), 'w+') as f:
            json.dump(self.pp_json_object, f, indent=4)
            f.close()

        return dataHandler.get_temp_file(self.__PP_JSON_FILE)

    def __build_json(self, elements):
        """Build the JSON formatted object.
        :param elements: dict of elements.
        """
        for elem in elements.values():
            if elem['sim_model'] == 'PyPower.RefBus':
                self.pp_json_object['bus'].insert(
                    0, [elem['elem_id'], elem['params']['bus_type'], elem['params']['base_kv']])
            elif elem['sim_model'] == 'PyPower.PQBus':
                self.pp_json_object['bus'].append(
                    [elem['elem_id'], elem['params']['bus_type'], elem['params']['base_kv']])
            elif elem['sim_model'] == 'PyPower.Transformer':
                self.pp_json_object['trafo'].append(
                    [elem['elem_id'], elem['params']['fbus'], elem['params']['tbus'], elem['params']['ttype'],
                     elem['params']['online'], elem['params']['tap']])
            elif elem['sim_model'] == 'PyPower.Branch':
                self.pp_json_object['branch'].append(
                    [elem['elem_id'], elem['params']['fbus'], elem['params']['tbus'], elem['params']['btype'],
                     elem['params']['l'], elem['params']['online']])