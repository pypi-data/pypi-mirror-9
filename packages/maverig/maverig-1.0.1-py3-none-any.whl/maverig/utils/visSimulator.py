import arrow
import mosaik_api
from dateutil import tz

meta = {
    'models': {
        'Topology': {
            'public': True,
            'params': [],
            'attrs': [],
            'any_inputs': True,
        },
    },
    'extra_methods': [],
}

DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'


class VisSimulator(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta)
        self.start_date = None
        self.step_size = None
        self.sim_proxy = None
        self.elements = None
        self.sid = None
        self.eid = None

    def init(self, sid, start_date, step_size, sim_proxy, elements):
        """Initialize the simulator with the ID *sid*, the start date *start_date*, the step size *step_size*,
        the simulation proxy *sim_proxy* and the elements list *elements*.
        """
        self.sid = sid
        dt = arrow.parser.DateTimeParser().parse(start_date, DATE_FORMAT)
        self.start_date = arrow.get(dt, tz.tzlocal()).isoformat()
        self.step_size = step_size
        self.sim_proxy = sim_proxy
        self.elements = elements

        return self.meta

    def create(self, num, model):
        """Create *num* instances of *model*."""
        if num != 1 or self.eid is not None:
            raise ValueError('Can only create one visualization topology model.')
        if model != 'Topology':
            raise ValueError('Unknown model: "%s"' % model)

        self.eid = 'vis_sim'

        return [{'eid': self.eid, 'type': model, 'rel': []}]

    def step(self, time, inputs):
        """Perform the next simulation step from time *time* using input values
        from *inputs*, update the simulation data (time, progress, element values) via the simulation proxy and
         return the new simulation time (the time at which ``step()`` should be called again).
        """
        inputs = inputs[self.eid]

        progress = yield self.mosaik.get_progress()
        elem_data = {}
        for elem in self.elements.values():
            mosaik_full_id = elem['mosaik_full_id']
            elem_data[mosaik_full_id] = {}
            for attr_name in elem['attrs']:
                val = None
                try:
                    val = inputs[attr_name][mosaik_full_id]
                except KeyError:
                    if attr_name in elem['params']:
                        # pass param to attribute
                        val = elem['params'][attr_name]

                elem_data[mosaik_full_id][attr_name] = val

        self.sim_proxy.update_data(time, progress, elem_data)

        return time + self.step_size


def main():
    return mosaik_api.start_simulation(VisSimulator())


if __name__ == '__main__':
    main()