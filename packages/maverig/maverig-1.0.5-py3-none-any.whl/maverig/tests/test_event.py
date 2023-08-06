from unittest import TestCase
from maverig.utils.event import Event


class TestEvent(TestCase):

    def test_handle(self):
        data_changed = Event()
        data_changed += self.on_data_changed  # handle
        data_changed += self.on_data_changed  # handle twice of same function has no effect
        assert len(data_changed) == 1  # function only registered once

    def test_unhandle(self):
        data_changed = Event()

        data_changed += self.on_data_changed  # handle
        assert len(data_changed) == 1

        data_changed -= self.on_data_changed  # unhandle
        assert len(data_changed) == 0

        self.assertRaises(ValueError, data_changed.unhandle, self.on_data_changed)  # cannot unhandle twice
        assert len(data_changed) == 0

    def test_fire(self):
        data_changed = Event()

        data_changed += self.on_data_changed  # handle

        param1 = 2
        data_changed(param1, param2=3)  # fire

    def on_data_changed(self, param1, param2):
        assert param1 == 2 and param2 == 3