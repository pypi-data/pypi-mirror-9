from functools import partial

from PySide import QtCore, QtGui, QtSvg
from PySide.QtCore import Qt

from maverig.data import dataHandler
from maverig.utils.flowlayout import FlowLayout
from maverig.views import abstractView


class ModePanelView(QtGui.QScrollArea, abstractView.AbstractView):
    """Represents the mode panel. A component can be added by activating the necessary comp mode in the
    scenarioPanel. A comp mode can be activated by clicking on the appropriate button."""

    def __init__(self):
        super(ModePanelView, self).__init__()

        self.btn_hide = None
        self.v_layout = None
        self.pane_grid = None
        self.scroll_area = None
        self.pane_vbox = None
        self.tmpBtn = None
        self.btn_selection_mode = None
        self.btn_hand_mode = None
        self.btn_add_component = None
        self.grid_layout = None

        self.component_header = None
        self.header_layout = None
        self.header_label = None

        self.button_group = None
        self.componentButtons = None

        self.context_menu = None
        self.action_delete = None
        self.action_hide = None
        self.action_show_invisible = None
        self.action_restore_components = None

    def init_ui(self):
        self.tmpBtn = None

        # size
        s_policy_comp_panel = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        s_policy_comp_panel.setVerticalStretch(1)
        self.setSizePolicy(s_policy_comp_panel)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # header
        self.header_label = QtGui.QLabel(_("Mode"))
        self.header_label.setStyleSheet("padding: 0px; color: #fdfdfd")

        self.header_layout = QtGui.QGridLayout()
        self.header_layout.addWidget(self.header_label, 0, QtCore.Qt.AlignLeft)

        self.btn_hide = QtGui.QPushButton()
        self.btn_hide.setStyleSheet("background-color: white; height: 25px; width: 25px; margin-top:-1px")
        self.btn_hide.setIcon(QtGui.QIcon(dataHandler.get_icon("console/close_icon_3.png")))
        self.btn_hide.clicked.connect(self.associated_presenter.on_change_visibility_triggered)
        self.header_layout.addWidget(self.btn_hide, 0, QtCore.Qt.AlignVCenter, QtCore.Qt.AlignRight)

        self.component_header = QtGui.QFrame()
        self.component_header.setStyleSheet("background: #484848; padding: -5px")
        self.component_header.setLayout(self.header_layout)
        s_policy_component_header = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.component_header.setSizePolicy(s_policy_component_header)

        # component buttons
        self.componentButtons = []
        self.button_group = QtGui.QButtonGroup()

        # layouts
        self.grid_layout = QtGui.QGridLayout()

        # hand mode / selection mode buttons
        layout = self.create_category_layout('')
        self.btn_selection_mode = self.create_button(dataHandler.get_icon('selection_mode.svg'), _("selection mode"))
        self.btn_selection_mode.clicked.connect(self.associated_presenter.selection_mode_btn_clicked)
        self.btn_selection_mode.setShortcut(QtGui.QKeySequence("ESC"))
        self.button_group.addButton(self.btn_selection_mode)
        layout.addWidget(self.btn_selection_mode)

        self.btn_hand_mode = self.create_button(dataHandler.get_icon('hand_mode.svg'), _("hand mode"))
        self.btn_hand_mode.clicked.connect(self.associated_presenter.hand_mode_btn_clicked)
        self.button_group.addButton(self.btn_hand_mode)
        layout.addWidget(self.btn_hand_mode)

        # add component type button
        self.btn_add_component = self.create_button(dataHandler.get_icon('add_component.svg'), _("add component"))
        self.btn_add_component.clicked.connect(self.associated_presenter.add_component_btn_clicked)
        self.button_group.addButton(self.btn_add_component)
        layout.addWidget(self.btn_add_component)

        # component buttons
        self.create_components_grid(self.associated_presenter.get_published_components())

        self.pane_grid = QtGui.QWidget()
        self.pane_grid.setLayout(self.grid_layout)
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setFrameStyle(QtGui.QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.pane_grid)

        self.v_layout = QtGui.QVBoxLayout()
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.addWidget(self.component_header)
        self.v_layout.addWidget(self.scroll_area)

        self.pane_vbox = QtGui.QWidget()
        self.pane_vbox.setLayout(self.v_layout)

        self.setWidget(self.pane_vbox)

    def create_components_grid(self, published_components):
        """ return a grid layout with components according to component configuration """
        # layout of horizontal groupboxes for each category
        category_layouts = {}

        for comp_name, category, icon_path, tooltip, transparency in published_components:
            # access groupbox with layout; create it if necessary
            category = _(category)
            tooltip = _(tooltip)
            if category in category_layouts:
                layout = category_layouts[category]
            else:
                layout = self.create_category_layout(category)
                category_layouts[category] = layout

            # create toggle-button
            btn = self.create_button(icon_path, tooltip, transparency)
            self.componentButtons.append(btn)
            self.button_group.addButton(btn)

            # presenter notifications
            btn.clicked.connect(partial(self.associated_presenter.comp_btn_clicked, btn, comp_name))
            btn.mousePressEvent = partial(self.button_mouse_pressed, btn, comp_name)
            btn.mouseMoveEvent = partial(self.button_mouse_move, btn, comp_name)
            self.associated_presenter.comp_btn_created(btn, comp_name)

            # add button to grid layout
            layout.addWidget(btn)

    def create_category_layout(self, category):
        gb = QtGui.QGroupBox(category)
        gb.sizePolicy()
        gb.setStyleSheet("font-weight: bold")
        self.grid_layout.addWidget(gb)
        layout = FlowLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        gb.setLayout(layout)
        return layout

    def uncheck_buttons(self):
        """ uncheck all buttons """
        # create invisible temp button which is selected when toggled button is clicked again
        btn_tmp = QtGui.QPushButton()
        btn_tmp.setCheckable(True)
        btn_tmp.setHidden(True)
        self.button_group.addButton(btn_tmp)
        self.button_group.setExclusive(True)
        btn_tmp.setChecked(True)
        self.button_group.removeButton(btn_tmp)

    def create_button(self, icon_path, tooltip, transparency=False, btn_w=55, btn_h=55, icn_w=35, icn_h=35):
        """
        :param icon_path: complete icon path
        :param tool_tip: description of the button
        :param btn_w: button width
        :param btn_h: button high
        :param icn_w: icon widht
        :param icn_h: icon high
        :return: qpushbutton
        """
        btn = QtGui.QPushButton()
        btn.setMinimumSize(btn_w, btn_h)
        btn.setMaximumSize(btn_w, btn_h)
        btn.setStyleSheet("border: thin; margin: 0px; padding: 0px;")

        self.set_svg_icon(btn, icon_path, icn_w, icn_h)

        btn.setToolTip(tooltip)
        btn.setCheckable(True)

        if transparency:
            effect = QtGui.QGraphicsOpacityEffect()
            effect.setOpacity(0.5)
            btn.effect = effect  # store effect so that it doesn't get lost by garbage collection
            btn.setGraphicsEffect(effect)

        # set additional fields
        btn.icon_path = icon_path
        return btn

    def button_mouse_move(self, btn, comp_name, mouse_event):
        mimedata = QtCore.QMimeData()

        drag = QtGui.QDrag(btn)
        mimedata.setText(comp_name)
        drag.setMimeData(mimedata)
        drag.setPixmap(btn.icon().pixmap(QtCore.QSize(55, 55)))
        drag.setHotSpot(mouse_event.pos() - btn.rect().topLeft())
        self.associated_presenter.drag_started(btn, comp_name)
        drag.start(QtCore.Qt.MoveAction)
        super(btn.__class__, btn).mouseMoveEvent(mouse_event)

    def button_mouse_pressed(self, btn, comp_name, mouse_event):
        super(btn.__class__, btn).mousePressEvent(mouse_event)
        if mouse_event.button() == QtCore.Qt.RightButton:
            self.associated_presenter.on_btn_context_menu(mouse_event, comp_name)

    @staticmethod
    def set_svg_icon(btn, icon_path, width, height):
        """ draws an svg icon on button btn """
        image = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32_Premultiplied)
        image.fill(QtCore.Qt.transparent)
        if icon_path.endswith('.svg'):
            renderer = QtSvg.QSvgRenderer(icon_path)
            renderer.render(QtGui.QPainter(image))
        else:
            image.load(icon_path)

        btn.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(image)))
        btn.setIconSize(QtCore.QSize(width, height))

    def hover_component_button(self, btn, icn_w=55, icn_h=55):
        """ if a component button has been selected it will increase its size """

        if self.tmpBtn and self.tmpBtn is not btn:
            self.unhover_component_button(self.tmpBtn)

        self.set_svg_icon(btn, btn.icon_path, icn_w, icn_h)
        self.tmpBtn = btn

    def unhover_component_button(self, btn, icn_w=35, icn_h=35):
        """ if a component button has been deselected it will get a smaller size """
        self.set_svg_icon(btn, btn.icon_path, icn_w, icn_h)

    def contextMenuEvent(self, event):
        if not isinstance(self.childAt(event.pos()), QtGui.QPushButton):
            super().contextMenuEvent(event)
            self.associated_presenter.on_context_menu(event)

    def create_btn_context_menu(self):
        self.context_menu = QtGui.QMenu()

        self.action_delete = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/delete.png')),
                                           _('Remove component'), self)
        self.action_delete.triggered.connect(self.associated_presenter.remove_selected_component)
        self.context_menu.addAction(self.action_delete)

        self.action_hide = QtGui.QAction(_('Hide component'), self)
        self.action_hide.triggered.connect(self.associated_presenter.hide_selected_component)
        self.action_hide.setCheckable(True)
        self.context_menu.addAction(self.action_hide)

        return self.context_menu

    def create_context_menu(self):
        self.context_menu = QtGui.QMenu()

        self.action_show_invisible = QtGui.QAction(_('Show invisible components'), self)
        self.action_show_invisible.triggered.connect(self.associated_presenter.show_invisible_components)
        self.action_show_invisible.setCheckable(True)
        self.context_menu.addAction(self.action_show_invisible)

        self.action_restore_components = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('menubar/restore.png')),
                                                       _('Restore default components'), self)
        self.action_restore_components.triggered.connect(self.associated_presenter.restore_default_components)
        self.context_menu.addAction(self.action_restore_components)

        return self.context_menu