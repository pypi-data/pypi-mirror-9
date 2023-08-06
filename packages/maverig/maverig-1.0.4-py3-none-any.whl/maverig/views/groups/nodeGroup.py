from maverig.views.groups.abstractGroup import AbstractGroup
from maverig.views.items.circle import Circle


class NodeGroup(AbstractGroup):
    def __init__(self, positions):
        super().__init__()
        self.node = Circle(self, positions['0'], 'node')