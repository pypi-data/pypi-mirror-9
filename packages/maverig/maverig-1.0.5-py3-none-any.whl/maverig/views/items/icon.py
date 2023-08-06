from PySide import QtGui, QtSvg

from maverig.views.positioning.section import section_manager
from maverig.views.items.abstractItem import AbstractItem
from maverig.views.positioning.vPoint import VPoint, Change
from maverig.data import dataHandler


class Icon(AbstractItem):
    def __init__(self, parent_group, pos, icon_path):
        super().__init__(parent_group)
        self.__icon_path = icon_path
        self.init_graphics_item(icon_path)

        self.vp_center = VPoint(self)
        self.vp_center.pos = pos

        self.vp_movable = self.vp_center

    def init_graphics_item(self, icon_path):
        if icon_path.endswith('.svg'):
            self.graphics_item = QtSvg.QGraphicsSvgItem(icon_path, parent=None)
        else:
            self.graphics_item = QtGui.QGraphicsPixmapItem(QtGui.QPixmap(icon_path))
        size = 40
        self.graphics_item.setScale(size / self.graphics_item.boundingRect().width())
        self.graphics_item.translate(-0.5 * size, -0.5 * size)

        super().init_graphics_item()

    @property
    def icon_path(self):
        return self.__icon_path

    @icon_path.setter
    def icon_path(self, value):
        if self.__icon_path != value:
            self.__icon_path = value

            scene = self.graphics_item.scene()
            scene.blockSignals(True)  # avoid side effects

            old_graphics_item = self.graphics_item
            self.init_graphics_item(value)

            # TODO: copy property settings (enabled, visible...) of old_graphics_item to self.graphics_item

            self.graphics_item.setPos(old_graphics_item.pos())
            scene.addItem(self.graphics_item)
            scene.removeItem(old_graphics_item)
            scene.blockSignals(False)

    def move_pos(self, delta):
        self.vp_center.move_pos(delta, Change.moved)

    def on_position_changed(self, vp, delta, change, section):
        if section == section_manager.item_section:
            self.graphics_item.setPos(self.graphics_item.pos() + delta)