from PySide.QtGui import QGraphicsItem, QGraphicsRectItem
from PySide import QtGui, QtCore

from maverig.utils.event import Event


class AbstractItem():
    def __init__(self, parent_group):
        self.graphics_item = QGraphicsItem
        self.consumer_bar = QGraphicsRectItem()
        self.consumer_bar_bg = QGraphicsRectItem()
        self.producer_bar = QGraphicsRectItem()
        self.producer_bar_bg = QGraphicsRectItem()
        self.state_of_charge_bar = QGraphicsRectItem()
        self.state_of_charge_bar_bg = QGraphicsRectItem()
        self.state_of_charge_tip = QGraphicsRectItem()
        self.state_of_charge_tip_bg = QGraphicsRectItem()

        self.position_changed = Event()
        self.position_changed += self.on_position_changed
        self.v_points = []
        self.parent_group = parent_group
        self.parent_group.add_item(self)

    def init_graphics_item(self):
        """ post initialization of graphics_item.
        This method needs to be called after graphics_item initialization in subclasses. """
        self.graphics_item.related_item = self
        self.graphics_item.setFlag(self.graphics_item.ItemSendsGeometryChanges)
        self.graphics_item.setFlag(self.graphics_item.ItemSendsScenePositionChanges)
        self.graphics_item.setFlag(self.graphics_item.ItemIsMovable, False)  # custom move on mouseMoveEvent

        self.z_value = 100
        self.selectable = True

    def add_to_scene(self, scene):
        scene.addItem(self.graphics_item)

    def add_v_point(self, v_point):
        v_point.position_changed += self.position_changed
        self.v_points.append(v_point)

    @property
    def z_value(self):
        return self.graphics_item.zValue()

    @z_value.setter
    def z_value(self, value):
        self.graphics_item.setZValue(value)

    @property
    def visible(self):
        return self.graphics_item.isVisible()

    @visible.setter
    def visible(self, value):
        self.graphics_item.setVisible(value)

    @property
    def enabled(self):
        return self.graphics_item.isEnabled()

    @enabled.setter
    def enabled(self, value):
        self.graphics_item.setEnabled(value)

    @property
    def opacity(self):
        return self.graphics_item.opacity()

    @opacity.setter
    def opacity(self, value):
        self.graphics_item.setOpacity(value)

    def set_color_effect(self, color, transparency):
        self.clear_effects()
        effect = QtGui.QGraphicsColorizeEffect(self.graphics_item.scene())
        effect.setColor(color)
        effect.setStrength(transparency)
        self.graphics_item.setGraphicsEffect(effect)

    def set_shadow_effect(self, color, shadow_faint, offset1, offset2):
        self.clear_effects()
        shadow = QtGui.QGraphicsDropShadowEffect(self.graphics_item.scene())
        shadow.setColor(color)
        shadow.setBlurRadius(shadow_faint)
        shadow.setOffset(offset1, offset2)
        self.graphics_item.setGraphicsEffect(shadow)

    def clear_effects(self):
        self.graphics_item.setGraphicsEffect(None)
        if self.graphics_item.scene() is self.consumer_bar.scene():
            self.graphics_item.scene().removeItem(self.consumer_bar_bg)
            self.graphics_item.scene().removeItem(self.consumer_bar)
        elif self.graphics_item.scene() is self.producer_bar.scene():
            self.graphics_item.scene().removeItem(self.producer_bar_bg)
            self.graphics_item.scene().removeItem(self.producer_bar)

    def clear_state_of_charge_effect(self):
        if self.graphics_item.scene() is self.state_of_charge_bar.scene():
            self.graphics_item.scene().removeItem(self.state_of_charge_bar_bg)
            self.graphics_item.scene().removeItem(self.state_of_charge_bar)

    def clear_state_of_charge_tip(self):
        if self.graphics_item.scene() is self.state_of_charge_tip.scene():
            self.graphics_item.scene().removeItem(self.state_of_charge_tip)

    def clear_state_of_charge_tip_bg(self):
        if self.graphics_item.scene() is self.state_of_charge_tip_bg.scene():
            self.graphics_item.scene().removeItem(self.state_of_charge_tip_bg)

    def set_consumer_bar_effect(self, color, pos, width, height):
        self.clear_effects()

        self.consumer_bar_bg = QGraphicsRectItem(pos.x() - 19, pos.y() - 21 - height, 38, height)
        self.consumer_bar_bg.setPen(QtGui.QColor(0, 0, 0, 0))
        self.consumer_bar_bg.setBrush(QtGui.QColor(185, 185, 185))
        self.consumer_bar_bg.setZValue(1500)

        self.consumer_bar = QGraphicsRectItem(pos.x() - 19, pos.y() - 21 - height, width, height)
        self.consumer_bar.setPen(QtGui.QColor(0, 0, 0, 0))
        self.consumer_bar.setBrush(color)
        self.consumer_bar.setZValue(1500)

        self.graphics_item.scene().addItem(self.consumer_bar_bg)
        self.graphics_item.scene().addItem(self.consumer_bar)

    def set_producer_bar_effect(self, color, pos, width, height):
        self.clear_effects()

        self.producer_bar_bg = QGraphicsRectItem(pos.x() - 19, pos.y() + 26 - height, 38, height)
        self.producer_bar_bg.setPen(QtGui.QColor(0, 0, 0, 0))
        self.producer_bar_bg.setBrush(QtGui.QColor(185, 185, 185))
        self.producer_bar_bg.setZValue(1500)

        self.producer_bar = QGraphicsRectItem(pos.x() - 19, pos.y() + 26 - height, width, height)
        self.producer_bar.setPen(QtGui.QColor(0, 0, 0, 0))
        self.producer_bar.setBrush(color)
        self.producer_bar.setZValue(1500)

        self.graphics_item.scene().addItem(self.producer_bar_bg)
        self.graphics_item.scene().addItem(self.producer_bar)

    def set_state_of_charge_bar(self, color, pos, width, height):
        self.clear_state_of_charge_effect()
        self.clear_state_of_charge_tip()

        self.state_of_charge_bar_bg = QGraphicsRectItem(pos.x() - 12, pos.y() + 1 - height, 23, height)
        self.state_of_charge_bar_bg.setPen(QtGui.QColor(0, 0, 0, 0 ))
        self.state_of_charge_bar_bg.setBrush(QtGui.QColor(185, 185, 185))
        self.state_of_charge_bar_bg.setZValue(1501)

        self.state_of_charge_bar = QGraphicsRectItem(pos.x() - 12, pos.y() + 1 - height, width, height)
        self.state_of_charge_bar.setPen(QtGui.QColor(0, 0, 0, 0))
        self.state_of_charge_bar.setBrush(color)
        self.state_of_charge_bar.setZValue(1502)

        self.graphics_item.scene().addItem(self.state_of_charge_bar_bg)
        self.graphics_item.scene().addItem(self.state_of_charge_bar)

    def set_state_of_charge_tip(self, color, pos, width, height):
        self.clear_state_of_charge_tip()

        self.state_of_charge_tip = QGraphicsRectItem(pos.x() + 10, pos.y() - 2 - height, width, height)
        self.state_of_charge_tip.setPen(QtGui.QColor(0, 0, 0, 0))
        self.state_of_charge_tip.setBrush(color)
        self.state_of_charge_tip.setZValue(1501)

        self.graphics_item.scene().addItem(self.state_of_charge_tip)

    def set_state_of_charge_tip_bg(self, color, pos, width, height):
        self.clear_state_of_charge_tip_bg()

        self.state_of_charge_tip_bg = QGraphicsRectItem(pos.x() + 10, pos.y() - 2 - height, width, height)
        self.state_of_charge_tip_bg.setPen(QtGui.QColor(0, 0, 0, 0 ))
        self.state_of_charge_tip_bg.setBrush(QtGui.QColor(185, 185, 185))
        self.state_of_charge_tip_bg.setZValue(1500)

        self.graphics_item.scene().addItem(self.state_of_charge_tip_bg)

    @property
    def selected(self):
        return self.graphics_item.isSelected()

    @selected.setter
    def selected(self, value):
        self.graphics_item.setSelected(value)

    @property
    def selectable(self):
        return bool(self.graphics_item.ItemIsSelectable & self.graphics_item.flags())

    @selectable.setter
    def selectable(self, value):
        self.graphics_item.setFlag(self.graphics_item.ItemIsSelectable, value)

    @property
    def is_under_mouse(self):
        return self.graphics_item.isUnderMouse()

    def move_pos(self, delta):
        pass

    def on_position_changed(self, vp, delta):
        pass

    def remove(self):
        # loose dockings
        for vp in self.v_points:
            for other_vp in vp.extern_followers:
                vp.unfix(other_vp)
        scene = self.graphics_item.scene()
        scene.blockSignals(True)  # avoid side effects
        scene.removeItem(self.graphics_item)
        scene.blockSignals(False)
        self.parent_group.remove_item(self)