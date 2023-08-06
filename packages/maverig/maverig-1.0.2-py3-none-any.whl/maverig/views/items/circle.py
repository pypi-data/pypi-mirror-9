from PySide import QtCore, QtGui

from maverig.views.positioning.section import section_manager
from maverig.views.items.abstractItem import AbstractItem
from maverig.views.positioning.vPoint import VPoint, Change


class Circle(AbstractItem):
    def __init__(self, parent_group, pos, style):
        super().__init__(parent_group)
        self.__circle_style = None

        self.init_graphics_item()

        self.vp_center = VPoint(self)
        self.vp_center.pos = pos

        self.vp_movable = self.vp_center

        self.circle_style = style

    def init_graphics_item(self):
        self.graphics_item = QtGui.QGraphicsEllipseItem()
        super().init_graphics_item()

    def move_pos(self, delta):
        self.vp_center.move_pos(delta, Change.moved)

    def on_position_changed(self, vp, delta, change, section):
        if section == section_manager.item_section:
            self.graphics_item.setPos(self.graphics_item.pos() + delta)

    @property
    def circle_style(self):
        return self.__circle_style

    @circle_style.setter
    def circle_style(self, style):
        self.__circle_style = style
        if style == 'node':
            brush = QtGui.QBrush(QtGui.QColor(90, 90, 90))
            pen = QtGui.QPen(QtGui.QColor(80, 80, 80))
            size = QtCore.QSizeF(20, 20)
        elif style == 'endpoint':
            brush = QtGui.QBrush(QtGui.QColor(200, 200, 200))
            pen = QtGui.QPen(QtGui.QColor(80, 80, 80))
            size = QtCore.QSizeF(10, 10)

        self.graphics_item.setBrush(brush)
        self.graphics_item.setPen(pen)

        rect = QtCore.QRectF()
        rect.setSize(size)
        rect.moveCenter(QtCore.QPointF())
        self.graphics_item.setRect(rect)
        self.graphics_item.setPos(self.vp_center.pos)