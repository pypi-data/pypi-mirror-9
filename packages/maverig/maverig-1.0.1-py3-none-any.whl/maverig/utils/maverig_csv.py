import arrow
import mosaik_api
from maverig.utils import numTools

""" An extended copy of mosaik-csv simulator with static and dynamic data support

Example:

House
--- static data ---
num_hh, res
3,      4
--- dynamic data ---
Date,                 P # [W]
2014-10-20 00:00:00,  1080.1
2014-10-20 00:15:00,  686.06
...
"""

__version__ = '1.0.2'

DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'


class CSV(mosaik_api.Simulator):
    def __init__(self):
        super().__init__({'models': {}})
        self.start_date = None
        self.next_date = None
        self.datafile = None
        self.next_row = None
        self.modelname = None
        self.static_attrs = []
        self.dynamic_attrs = []
        self.eids = []
        self.cache = None
        self.static_cache = {}

    def init(self, sid, sim_start, datafile):
        self.start_date = arrow.get(sim_start, DATE_FORMAT)
        self.next_date = self.start_date

        self.datafile = open(datafile)
        self.modelname = next(self.datafile).strip()

        # Get attribute names and strip optional comments
        row = next(self.datafile).strip()

        if 'static' in row:
            row = next(self.datafile).strip()
            self.static_attrs = [attr.split('#')[0].strip() for attr in row.split(',')]  # stripping comments

            row = next(self.datafile).strip()

            values = [numTools.convert(val) for val in row.split(',')]
            self.static_cache = dict(zip(self.static_attrs, values))

            row = next(self.datafile).strip()

        if 'dynamic' in row:
            row = next(self.datafile).strip()

        self.dynamic_attrs = [attr.split('#')[0].strip() for attr in row.split(',')[1:]]  # stripping comments

        self.meta['models'][self.modelname] = {
            'public': True,
            'params': [],
            'attrs': self.static_attrs + self.dynamic_attrs,
        }

        # Check start date
        self._read_next_row()
        if self.start_date < self.next_row[0]:
            raise ValueError('Start date "%s" not in CSV file.' %
                             self.start_date.format(DATE_FORMAT))
        while self.start_date > self.next_row[0]:
            self._read_next_row()
            if self.next_row is None:
                raise ValueError('Start date "%s" not in CSV file.' %
                                 self.start_date.format(DATE_FORMAT))

        return self.meta

    def create(self, num, model):
        if model != self.modelname:
            raise ValueError('Invalid model "%s" % model')

        start_idx = len(self.eids)
        entities = []
        for i in range(num):
            eid = '%s_%s' % (model, i + start_idx)
            entities.append({
                'eid': eid,
                'type': model,
                'rel': [],
            })
            self.eids.append(eid)
        return entities

    def step(self, time, inputs=None):
        data = self.next_row
        if data is None:
            raise IndexError('End of CSV file reached.')

        # Check date
        date = data[0]
        expected_date = self.start_date.replace(seconds=time)
        if date != expected_date:
            raise IndexError('Wrong date "%s", expected "%s"' % (
                date.format(DATE_FORMAT),
                expected_date.format(DATE_FORMAT)))

        # Put data into the cache for get_data() calls
        self.cache = {}
        for attr, val in zip(self.dynamic_attrs, data[1:]):
            self.cache[attr] = numTools.convert(val)

        self._read_next_row()
        if self.next_row is not None:
            return time + (self.next_row[0].timestamp - date.timestamp)
        else:
            return float('inf')

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            if eid not in self.eids:
                raise ValueError('Unknown entity ID "%s"' % eid)

            data[eid] = {}
            for attr in attrs:
                if attr in self.static_cache:
                    data[eid][attr] = self.static_cache[attr]
                else:
                    data[eid][attr] = self.cache[attr]

        return data

    def _read_next_row(self):
        try:
            self.next_row = next(self.datafile).strip().split(',')
            self.next_row[0] = arrow.get(self.next_row[0], DATE_FORMAT)
        except StopIteration:
            self.next_row = None


def main():
    return mosaik_api.start_simulation(CSV(), 'maverig-csv simulator')
