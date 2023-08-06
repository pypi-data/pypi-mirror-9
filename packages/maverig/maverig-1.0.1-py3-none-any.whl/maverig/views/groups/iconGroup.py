from maverig.views.groups.abstractGroup import AbstractGroup
from maverig.views.items.line import Line
from maverig.views.items.icon import Icon
from maverig.views.items.circle import Circle


class IconGroup(AbstractGroup):
    def __init__(self, positions, icon_path):
        """ creates an icon group with dotted lines connected to endpoints
        depending on the number of given positions """
        super().__init__()
        self.pos = positions['0']

        self.icon = Icon(self, self.pos, icon_path)

        self.lines = []
        self.endpoints = []

        for i in range(1, len(positions)):
            self.add_endpoint(positions[str(i)])

    def add_endpoint(self, endpoint_pos):
        """ add an endpoint with a dotted line to icon """
        dotted_line = Line(self, self.pos, endpoint_pos, 'dotted')
        endpoint = Circle(self, endpoint_pos, 'endpoint')

        self.endpoints.append(endpoint)
        self.lines.append(dotted_line)

        # stack under icon (z-value 100)
        dotted_line.z_value = 99
        endpoint.z_value = 99

        dotted_line.vp_left.fix(self.icon.vp_center)
        dotted_line.vp_right.fix(endpoint.vp_center)