import math

import numpy
from PySide import QtCore, QtGui
from maverig.data import dataHandler

from maverig.views import abstractView


class ScenarioPanelView(QtGui.QGraphicsView, abstractView.AbstractView):
    """Represents the scenario panel."""

    def __init__(self):
        super(ScenarioPanelView, self).__init__()
        self.scene = None

        self.action_cut = None
        self.action_copy = None
        self.action_paste = None
        self.action_delete = None
        self.action_select_all = None
        self.context_menu = None

    def init_ui(self):
        # style
        s_policy_scenario_panel = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        s_policy_scenario_panel.setHorizontalStretch(0)
        s_policy_scenario_panel.setVerticalStretch(2)
        self.setSizePolicy(s_policy_scenario_panel)
        self.setMinimumSize(QtCore.QSize(1, 1))

        # scene
        self.scene = QtGui.QGraphicsScene()
        self.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.scene.setSceneRect(0, 0, self.width(), self.height())
        self.setScene(self.scene)
        self.scene.changed.connect(self.associated_presenter.adjust_scene_rect)
        self.scene.selectionChanged.connect(self.associated_presenter.on_selection_changed)

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        self.associated_presenter.on_draw_background(painter)

    def paint_datetime(self, bgcolor_from, bgcolor_to):
        gradient = QtGui.QLinearGradient(QtCore.QPointF(0, (self.width() / 2)), QtCore.QPointF(self.height(),
                                                                                               (self.width() / 2)))
        gradient.setColorAt(0, QtGui.QColor(bgcolor_from, bgcolor_from, bgcolor_from))
        gradient.setColorAt(1, QtGui.QColor(bgcolor_to, bgcolor_to, bgcolor_to))
        self.setBackgroundBrush(gradient)

    def refreshBg(self):
        self.setBackgroundBrush(QtGui.QColor(255, 255, 255))
        self.associated_presenter.adjust_scene_rect()

    def draw_raster(self, cell_size, painter):
        """ draws a raster depending on the chosen cell size on the given painter device """

        # view_rect is the complete graphics view area (scene_rect can be a cutout of view_rect)
        view_rect = self.mapToScene(self.frameRect()).boundingRect()

        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)  # no antialiasing looks better for raster lines

        # vertical lines
        start_x = math.ceil(view_rect.left() / cell_size) * cell_size
        end_x = int(view_rect.right())
        top = view_rect.top()
        bottom = view_rect.bottom()

        # horizontal lines
        start_y = math.ceil(view_rect.top() / cell_size) * cell_size
        end_y = int(view_rect.bottom())
        left = view_rect.left()
        right = view_rect.right()

        # draw lines
        current_scale_factor = self.matrix().m11()
        size_factor = 1.0 / current_scale_factor

        lightness = 0.5 * math.pow(size_factor, 0.07)  # adapt color to scale. bigger size factor means lighter color
        lightness = numpy.clip(lightness, 0.75, 0.9)

        color = QtGui.QColor().fromHslF(0, 0, lightness)
        pen = QtGui.QPen(color)  # set line color
        pen.setWidthF(size_factor)
        painter.setPen(pen)

        for x in range(start_x, end_x, cell_size):
            painter.drawLine(x, top, x, bottom)
        for y in range(start_y, end_y, cell_size):
            painter.drawLine(left, y, right, y)

    def mouseDoubleClickEvent(self, event):
        super().mouseReleaseEvent(event)
        mouse_pos = self.mapToScene(event.pos())
        self.associated_presenter.select_all_active_elements(mouse_pos)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:  # workaround for context menu (only process left click)
            super().mousePressEvent(event)

        mouse_pos = self.mapToScene(event.pos())
        self.associated_presenter.mouse_clicked(mouse_pos, event.button())

    def mouseMoveEvent(self, event):
        """allow dragging newly created elements"""
        super().mouseMoveEvent(event)
        mouse_pos = self.mapToScene(event.pos())
        self.associated_presenter.mouse_moved(mouse_pos, event.buttons())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        mouse_pos = self.mapToScene(event.pos())
        self.associated_presenter.mouse_released(mouse_pos)

    def wheelEvent(self, wheel_event):
        if wheel_event.modifiers() == QtCore.Qt.CTRL:
            self.associated_presenter.zoom(wheel_event.delta() > 0, wheel_event)
        elif wheel_event.modifiers() == QtCore.Qt.SHIFT:
            self.horizontalScrollBar().event(wheel_event)
        else:
            super().wheelEvent(wheel_event)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        event.accept()
        mouse_pos = self.mapToScene(event.pos())
        mouse_pos_real = self.associated_presenter.damped_mouse_pos(mouse_pos)
        self.associated_presenter.mouse_moved(mouse_pos, QtCore.Qt.LeftButton)
        self.associated_presenter.mouse_clicked(mouse_pos, QtCore.Qt.LeftButton)
        self.associated_presenter.mouse_released(mouse_pos)

    def contextMenuEvent(self, event):
        super().contextMenuEvent(event)
        self.associated_presenter.on_context_menu(event)

    def create_context_menu(self):
        self.context_menu = QtGui.QMenu()
        self.action_cut = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/cut.png')),
                                              _('Cut'), self)
        self.action_cut.triggered.connect(self.associated_presenter.cut_selected_elements)
        self.context_menu.addAction(self.action_cut)

        self.action_copy = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/copy.png')),
                                               _('Copy'), self)
        self.action_copy.triggered.connect(self.associated_presenter.copy_selected_elements)
        self.context_menu.addAction(self.action_copy)

        self.action_paste = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/paste.png')),
                                                _('Paste'), self)
        self.action_paste.triggered.connect(self.associated_presenter.paste_elements)
        self.context_menu.addAction(self.action_paste)

        self.action_delete = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/delete.png')),
                                                 _('Delete'), self)
        self.action_delete.triggered.connect(self.associated_presenter.delete_selected_elements)
        self.context_menu.addAction(self.action_delete)

        self.action_select_all = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/select_all.png')),
                                               _('Select All'), self)
        self.action_select_all.triggered.connect(self.associated_presenter.select_all_elements)
        self.context_menu.addAction(self.action_select_all)
        return self.context_menu