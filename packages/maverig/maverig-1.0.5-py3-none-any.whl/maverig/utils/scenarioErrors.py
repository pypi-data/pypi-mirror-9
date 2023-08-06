

class ScenarioError(Exception):
    title = property(lambda self: _('Scenario Error'))
    console_text = property(lambda self: '')
    text = property(lambda self: '')
    info_text = property(lambda self: '')
    elem_ids = []


class ScenarioEmptyError(ScenarioError):
    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('An empty scenario cannot be simulated.')

    @property
    def text(self):
        return _('The scenario is empty.')

    @property
    def info_text(self):
        return _('An empty scenario cannot be simulated.')


class ScenarioOfflineElementError(ScenarioError):
    def __init__(self, elem_id=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]

    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('%s is offline') % self.elem_id

    @property
    def text(self):
        return _('The selected element is offline.')

    @property
    def info_text(self):
        return _('Please activate online parameter in property panel.')


class ScenarioConnectionError(ScenarioError):
    def __init__(self, elem_id=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]

    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('%s is disconnected.') % self.elem_id

    @property
    def text(self):
        return _('The selected element is disconnected.')

    @property
    def info_text(self):
        return _('Please dock loose endpoints to other elements.')


class ScenarioBaseVoltageLevelError(ScenarioError):
    def __init__(self, ref_id='', bus_id=''):
        self.ref_id = ref_id
        self.bus_id = bus_id
        self.elem_ids = [ref_id, bus_id]

    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('Base voltage level of {0} and {1} have to be equal.'.format(self.ref_id, self.bus_id))

    @property
    def text(self):
        return _('Base voltage level of the selected elements have to be equal.')

    @property
    def info_text(self):
        return _('Please adjust voltage level parameter in property panel.')


class ScenarioRefBusConnectionError(ScenarioError):
    def __init__(self, elem_id=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]

    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('%s is not connected correctly.') % self.elem_id

    @property
    def text(self):
        return _('The selected reference bus is not connected correctly.')

    @property
    def info_text(self):
        return _('A reference bus needs exactly one connected Branch.')


class ScenarioRefBusMissingError(ScenarioError):
    def __init__(self):
        self.elem_ids = []

    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('Missing reference bus.')

    @property
    def text(self):
        return _('Missing reference bus.')

    @property
    def info_text(self):
        return _('Create a reference bus from component panel.')


class ScenarioRefBusCountError(ScenarioError):
    def __init__(self, elem_ids=[]):
        self.elem_ids = elem_ids

    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('Too many reference buses %s' % str(tuple(self.elem_ids)))

    @property
    def text(self):
        return _('Only one reference bus is allowed.')

    @property
    def info_text(self):
        return _('Remove all except one of the selected reference buses from scenario.')


class ScenarioDatafileError(ScenarioError):
    def __init__(self, elem_id=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]

    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('%s has no valid datafile') % self.elem_id

    @property
    def text(self):
        return _('The selected element has no valid data file.')

    @property
    def info_text(self):
        return _('Please set datafile parameter in property panel.')


class ScenarioFileNotFoundError(ScenarioError):
    def __init__(self, elem_id='', sim_name='', filename=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]
        self.sim_name = sim_name
        self.filename = filename

    @property
    def title(self):
        return _('Maverig Scenario Error')

    @property
    def console_text(self):
        return _('Could not start Simulator {0} for element {1}.'.format(self.sim_name, self.elem_id)) + '\n' +\
               _('File "%s" not found.') % self.filename

    @property
    def text(self):
        return _('File "%s" not found for selected element.') % self.filename

    @property
    def info_text(self):
        return _('Please check file parameters in property panel.')


class ScenarioSimulatorError(ScenarioError):
    def __init__(self, elem_id='', sim_name='', tb=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]
        self.sim_name = sim_name
        self.tb = tb

    @property
    def title(self):
        return _('Mosaik Scenario Error')

    @property
    def console_text(self):
        return _('Could not start Simulator {0} for element {1}.'.format(self.sim_name, self.elem_id)) + '\n' + self.tb

    @property
    def text(self):
        return _('Could not start Simulator %s for selected element.') % self.sim_name

    @property
    def info_text(self):
        return _('See console output for exception traceback.')


class ScenarioComponentError(ScenarioError):
    def __init__(self, elem_id='', sim_model=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]
        self.sim_model = sim_model

    @property
    def title(self):
        return _('Maverig Component Error')

    @property
    def console_text(self):
        return _('Could not start element %s.' % self.elem_id) + '\n' + \
               _('Simulator metadata does not support model "%s"') % self.sim_model

    @property
    def text(self):
        return _('Could not start selected element.') + ' ' + \
               _('Simulator metadata does not support model "%s"') % self.sim_model

    @property
    def info_text(self):
        return _('Please check model part of sim_model in component JSON file.')


class ScenarioElementError(ScenarioError):
    def __init__(self, elem_id='', tb=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]
        self.tb = tb

    @property
    def title(self):
        return _('Mosaik Scenario Error')

    @property
    def console_text(self):
        return _('Could not start element %s.') % self.elem_id + '\n' + self.tb

    @property
    def text(self):
        return _('Could not start selected element')

    @property
    def info_text(self):
        return _('See console output for exception traceback.')


class ScenarioSimulationBranchLengthError(ScenarioError):
    def __init__(self, elem_id=''):
        self.elem_id = elem_id
        self.elem_ids = [elem_id]

    @property
    def title(self):
        return _('Maverig Simulation Error')

    @property
    def console_text(self):
        return _('Length of %s is too long and exceeds voltage boundaries!') % self.elem_id

    @property
    def text(self):
        return _('Length of selected branch is too long and exceeds voltage boundaries!')

    @property
    def info_text(self):
        return _('Simulation has been stopped. Please reduce parameter length in property panel.')


class ScenarioSimulationPowerflowError(ScenarioError):
    def __init__(self, elem_ids=[]):
        self.elem_ids = elem_ids

    @property
    def title(self):
        return _('Mosaik Simulation Error')

    @property
    def console_text(self):
        return _('PyPower powerflow calculation did not converge.')

    @property
    def text(self):
        return _('PyPower powerflow calculation did not converge.')

    @property
    def info_text(self):
        return _('Some of the selected branches might exceed voltage boundaries if they are too long.\n'
                 'Check length parameter in property panel.')


class ScenarioSimulationRuntimeError(ScenarioError):
    def __init__(self, tb=''):
        self.elem_ids = []
        self.tb = tb

    @property
    def title(self):
        return _('Mosaik Simulation Error')

    @property
    def console_text(self):
        return self.tb

    @property
    def text(self):
        return _('An error occured during simulation runtime.')

    @property
    def info_text(self):
        return _('See console output for exception traceback.')