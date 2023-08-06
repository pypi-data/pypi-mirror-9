from PySide import QtCore, QtGui

from maverig.views.positioning.section import section_manager
from maverig.views.positioning.vPoint import VPoint, Change
from maverig.views.items.abstractItem import AbstractItem


class Line(AbstractItem):
    def __init__(self, parent_group, start_pos, end_pos, line_style):
        super().__init__(parent_group)
        self.init_graphics_item()

        self.line_pos = QtCore.QPointF()

        self.line_style = line_style

        self.vp_left = VPoint(self)
        self.vp_center = VPoint(self)
        self.vp_right = VPoint(self)
        self.vp_left.pos = start_pos
        self.vp_right.pos = end_pos
        self.vp_center.pos = (start_pos + end_pos) / 2

        self.vp_movable = self.vp_center

    def init_graphics_item(self):
        self.graphics_item = QtGui.QGraphicsLineItem()
        self.graphics_item.shape = self._shape
        super().init_graphics_item()

    def _shape(self):
        """ create bigger shape for line selection """
        path = QtGui.QPainterPath()
        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(15)
        path.moveTo(self.graphics_item.line().p1())
        path.lineTo(self.graphics_item.line().p2())
        return stroker.createStroke(path)

    def move_pos(self, delta):
        self.vp_movable.move_pos(delta, Change.moved)

    def on_position_changed(self, vp, delta, change, section):
        if section == section_manager.adjust_section and change != Change.calculated:

            center_is_moving = self.vp_center.new_pos != self.vp_center.pos and self.vp_center.change == Change.moved

            if vp == self.vp_center:
                with section_manager.pos_section:
                    self.vp_left.move_pos(delta, Change.calculated)
                    self.vp_right.move_pos(delta, Change.calculated)
            elif not center_is_moving:
                center_pos = (self.vp_left.new_pos + self.vp_right.new_pos) / 2
                self.vp_center.set_pos(center_pos, Change.calculated)

        if section == section_manager.item_section:
            self.adjust_line()

    def adjust_line(self):
        """ adjusts the line position to the endpoints. """
        qline = QtCore.QLineF(self.vp_left.pos - self.line_pos, self.vp_right.pos - self.line_pos)
        self.graphics_item.prepareGeometryChange()
        self.graphics_item.setLine(qline)

    @property
    def line_style(self):
        if self.graphics_item.pen().style() == QtCore.Qt.DotLine:
            return 'dotted'
        else:
            return 'solid'

    @line_style.setter
    def line_style(self, value):
        pen = QtGui.QPen(QtGui.QColor(72, 72, 72))
        pen.setWidth(3)

        if value == 'dotted':
            pen.setStyle(QtCore.Qt.DotLine)
        elif value == 'offline':
            pen.setColor(QtGui.QColor(181, 36, 36))
        else:
            pen.setStyle(QtCore.Qt.SolidLine)
        self.graphics_item.setPen(pen)
