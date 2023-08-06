import gettext
from functools import partial

from PySide import QtCore, QtGui, QtSvg
from PySide.QtCore import Qt

from maverig.views import abstractView
from maverig.data import dataHandler


class PropertyPanelView(QtGui.QScrollArea, abstractView.AbstractView):
    """Represents the property panel. Every component has specific properties which are displayed within this panel. The
    user can change the properties of every single component within this panel.
    """

    def __init__(self):
        super(PropertyPanelView, self).__init__()

        self.btn_hide = None
        self.v_layout = None
        self.grid_layout = None
        self.pane_grid = None

        self.property_header = None
        self.header_layout = None
        self.header_label = None
        self.households_label = None

        self.pane_vbox = None
        self._property_value_objects = None

    def init_ui(self):
        # size
        s_policy_prop_panel = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        s_policy_prop_panel.setHorizontalStretch(0)
        s_policy_prop_panel.setVerticalStretch(2)
        self.setSizePolicy(s_policy_prop_panel)
        self.setMinimumSize(1, 1)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # header
        self.header_label = QtGui.QLabel(_("Properties"))
        self.header_label.setStyleSheet("padding: 0px; color: #fdfdfd")

        self.header_layout = QtGui.QGridLayout()
        self.header_layout.addWidget(self.header_label, 0, QtCore.Qt.AlignLeft)

        self.btn_hide = QtGui.QPushButton()
        self.btn_hide.setStyleSheet("background-color: white; height: 26px; width: 25px; margin-top:-1px")
        self.btn_hide.setIcon(QtGui.QIcon(dataHandler.get_icon("console/close_icon_3.png")))
        self.btn_hide.clicked.connect(self.associated_presenter.on_change_visibility_triggered)
        self.header_layout.addWidget(self.btn_hide, 0, QtCore.Qt.AlignVCenter, QtCore.Qt.AlignRight)

        self.property_header = QtGui.QFrame()
        self.property_header.setStyleSheet("background: #484848; padding: -5px")
        self.property_header.setLayout(self.header_layout)
        s_policy_property_header = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.property_header.setSizePolicy(s_policy_property_header)

        # layouts
        self.grid_layout = QtGui.QGridLayout()

        self.pane_grid = QtGui.QWidget()
        self.pane_grid.setLayout(self.grid_layout)
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setFrameStyle(QtGui.QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.pane_grid)

        self.v_layout = QtGui.QVBoxLayout()
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.addWidget(self.property_header)
        self.v_layout.addWidget(self.scroll_area)

        self.pane_vbox = QtGui.QWidget()
        self.pane_vbox.setLayout(self.v_layout)

        self.setWidget(self.pane_vbox)

        self._property_value_objects = []

    def create_property_label(self, label, row):
        self.grid_layout.addWidget(QtGui.QLabel(_(label)), row, 0)

    def create_property_icon(self, icon_path, row):
        btn = QtGui.QPushButton()
        btn.setMinimumSize(35, 35)
        btn.setMaximumSize(35, 35)
        btn.setStyleSheet("border: thin; margin: 0px; padding: 0px;")

        self.set_svg_icon(btn, icon_path, 35, 35)

        self.grid_layout.addWidget(btn, row, 0)

    """ deletes a widget of the property panel associated to the given index """

    def delete_grid_widget(self, index):
        item = self.grid_layout.itemAt(index)
        if item is not None:
            widget = item.widget()
            if widget is not None:
                self.grid_layout.removeWidget(widget)
                widget.deleteLater()

    def clear_prop_grid(self):
        self.grid_layout = QtGui.QGridLayout()
        self.pane_grid = QtGui.QWidget()
        self.pane_grid.setLayout(self.grid_layout)
        s_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        s_policy.setVerticalStretch(0)
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setFrameStyle(QtGui.QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(s_policy)
        self.scroll_area.setWidget(self.pane_grid)
        self.v_layout = QtGui.QVBoxLayout()
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.addWidget(self.property_header)
        self.v_layout.addWidget(self.scroll_area)
        self.pane_vbox = QtGui.QWidget()
        self.pane_vbox.setLayout(self.v_layout)
        self.setWidget(self.pane_vbox)

    def create_integer_property_cell(self, label, value, row, accepted_values):
        s_box = QtGui.QSpinBox()
        s_box.setToolTip(_("Insert an integer to define the property value for ") + label)
        s_box.setWrapping(True)
        s_box.setMaximum(10000)
        if accepted_values is not None:
            s_box.setRange(accepted_values[0], accepted_values[len(accepted_values) - 1])
        s_box.setValue(value)
        self.add_property_value_object(s_box)
        self.grid_layout.addWidget(s_box, row, 1)
        s_box.setKeyboardTracking(False)
        s_box.valueChanged.connect(partial(self.associated_presenter.value_changed, s_box))
        s_box.valueChanged.connect(partial(self.associated_presenter.check_spinbox, s_box))
        return s_box

    def create_float_property_cell(self, label, value, row, accepted_values):
        s_box = QtGui.QDoubleSpinBox()
        s_box.setToolTip(_("Insert a float to define the property value for ") + label)
        s_box.setSingleStep(0.1)
        s_box.setMaximum(10000)
        s_box.setValue(value)
        if accepted_values is not None:
            s_box.setRange(accepted_values[0], accepted_values[len(accepted_values) - 1])
        s_box.setWrapping(True)
        self.add_property_value_object(s_box)
        self.grid_layout.addWidget(s_box, row, 1)
        s_box.setKeyboardTracking(False)
        s_box.valueChanged.connect(partial(self.associated_presenter.value_changed, s_box))
        s_box.valueChanged.connect(partial(self.associated_presenter.check_spinbox, s_box))
        return s_box

    def create_str_property_cell(self, label, value, row, accepted_values):
        if accepted_values:
            l_edit = QtGui.QComboBox()
            l_edit.addItems(accepted_values)
            l_edit.setCurrentIndex(accepted_values.index(value))
            l_edit.currentIndexChanged.connect(partial(self.associated_presenter.value_changed, l_edit))
        else:
            l_edit = QtGui.QLineEdit()
            l_edit.setText(value)
            l_edit.textChanged.connect(partial(self.associated_presenter.value_changed, l_edit))

        l_edit.setToolTip(_("Insert a string to define the property value for ") + label)
        self.add_property_value_object(l_edit)
        self.grid_layout.addWidget(l_edit, row, 1)
        return l_edit

    def create_household_cell(self, row, num_hh):
        hh_label = _("Household")
        if num_hh != 1:
            hh_label = _("Households")
        self.households_label = QtGui.QLabel(str(num_hh) + " " + hh_label)
        self.grid_layout.addWidget(self.households_label, row, 1)
        return self.households_label

    def change_household_cell(self, row, num_hh):
        hh_label = _("Household")
        if num_hh != 1:
            hh_label = _("Households")
        self.households_label.setText(str(num_hh) + " " + hh_label)
        self.grid_layout.addWidget(self.households_label, row, 1)
        return self.households_label

    def alter_integer_property_cell(self, value, row):
        l_edit = self._property_value_objects[row]
        l_edit.setText(value)

    def create_boolean_property_cell(self, label, state, row):
        c_box = QtGui.QCheckBox()
        c_box.setToolTip(_("Choose if property " + label + "should be activated"))
        if state is True:
            c_box.setChecked(True)
        self.add_property_value_object(c_box)
        self.grid_layout.addWidget(c_box, row, 1)
        c_box.stateChanged.connect(partial(self.associated_presenter.value_changed, c_box))
        return c_box

    def alter_boolean_property_cell(self, row, state):
        c_box = self._property_value_objects[row]
        if state is True:
            c_box.setChecked(True)

    def create_file_property_cell(self, label, value, row):
        l_edit = QtGui.QLineEdit()
        l_edit.setToolTip(_("Shows the file path of the chosen ") + label)
        self.grid_layout.addWidget(l_edit, row, 1)
        c_pushbutton = QtGui.QPushButton(("..."))
        c_pushbutton.setToolTip(_("Select the path to a file"))
        c_pushbutton.setFixedSize(20, 20)
        c_pushbutton.clicked.connect(lambda: self.open_file_dialog(l_edit))
        l_edit.setText(value)
        l_edit.textChanged.connect(partial(self.associated_presenter.value_changed, l_edit))
        self.add_property_value_object(l_edit)
        self.grid_layout.addWidget(c_pushbutton, row, 2)
        return l_edit

    def alter_file_property_cell(self, row):
        l_edit = self._property_value_objects[row]
        l_edit.setText("")

    def add_property_value_object(self, l_edit):
        self._property_value_objects.append(l_edit)

    # open a file dialog and set the chosen path in the related qline edit
    def open_file_dialog(self, l_edit):
        path, filter = QtGui.QFileDialog.getOpenFileName(self, _("Open file"), '*.csv')
        if path != "":
            l_edit.setText(dataHandler.get_relpath(path))

    # when elements are selected initialize the counter
    def init_selection_counter(self, count):
        if count == 1:
            self.header_label.setText(str(count) + " " + _("selected item"))
        else:
            self.header_label.setText(str(count) + " " + _("selected items"))

    def change_color(self, widget, color):
        p = widget.palette()
        p.setColor(QtGui.QPalette.Base, QtGui.QColor(color))
        widget.setPalette(p)

    def set_new_accepted_value(self, widget, new_value):
        widget.setValue(new_value)

    def set_parameter_style(self, widget, multivalue):
        """ if multiple selected components have different values give a hint """
        if multivalue:
            widget.setStyleSheet("font-style: italic; color: silver")
            if isinstance(widget, QtGui.QCheckBox):
                widget.blockSignals(True)
                widget.setCheckState(QtCore.Qt.PartiallyChecked)
                widget.blockSignals(False)
        else:
            widget.setStyleSheet("font-style: normal; color: black")

    @property
    def property_grid(self):
        return self.grid_layout

    @property
    def property_value_objects(self):
        return self.property_value_objects

    @staticmethod
    def set_svg_icon(btn, icon_path, width, height):
        """ draws an svg icon on button btn """
        pixmap = QtGui.QPixmap(QtCore.QSize(width, height))
        pixmap.fill(QtCore.Qt.transparent)
        renderer = QtSvg.QSvgRenderer(icon_path)
        renderer.render(QtGui.QPainter(pixmap))
        btn.setIcon(QtGui.QIcon(QtGui.QPixmap(pixmap)))
        btn.setIconSize(QtCore.QSize(width, height))