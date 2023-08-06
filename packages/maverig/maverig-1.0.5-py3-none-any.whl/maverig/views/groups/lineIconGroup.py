from maverig.views.groups.abstractGroup import AbstractGroup
from maverig.views.items.circle import Circle
from maverig.views.items.icon import Icon
from maverig.views.items.line import Line


class LineIconGroup(AbstractGroup):
    def __init__(self, positions, icon_file):
        super().__init__()

        self.line = Line(self, positions['0'], positions['1'], 'dotted')
        self.line.visible = False

        self.line_left = Line(self, positions['0'], self.line.vp_center.pos, 'solid')
        self.line_left.vp_left.fix(self.line.vp_left)
        self.line_left.vp_right.fix(self.line.vp_center)
        self.line_left.vp_movable = self.line_left.vp_left

        self.line_right = Line(self, self.line.vp_center.pos, positions['1'], 'solid')
        self.line_right.vp_left.fix(self.line.vp_center)
        self.line_right.vp_right.fix(self.line.vp_right)
        self.line_right.vp_movable = self.line_right.vp_right

        self.endpoint_left = Circle(self, positions['0'], 'endpoint')
        self.endpoint_left.vp_center.fix(self.line.vp_left)

        self.endpoint_right = Circle(self, positions['1'], 'endpoint')
        self.endpoint_right.vp_center.fix(self.line.vp_right)

        self.icon = Icon(self, self.line.vp_center.pos, icon_file)
        self.icon.vp_center.fix(self.line.vp_center)

        self.lines = [self.line_left, self.line_right]
        self.endpoints = [self.endpoint_left, self.endpoint_right]