from maverig.views.groups.abstractGroup import AbstractGroup
from maverig.views.items.circle import Circle
from maverig.views.items.line import Line


class LineGroup(AbstractGroup):
    def __init__(self, positions):
        super().__init__()

        self.line = Line(self, positions['0'], positions['1'], 'solid')
        self.endpoint_left = Circle(self, positions['0'], 'endpoint')
        self.endpoint_right = Circle(self, positions['1'], 'endpoint')

        self.lines = [self.line]
        self.endpoints = [self.endpoint_left, self.endpoint_right]

        self.endpoint_left.vp_center.fix(self.line.vp_left)
        self.endpoint_right.vp_center.fix(self.line.vp_right)

        self.line_left = None
        self.line_right = None