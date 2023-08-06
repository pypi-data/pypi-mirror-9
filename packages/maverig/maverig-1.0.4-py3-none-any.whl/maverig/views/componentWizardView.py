import os
import re
import shutil
from PySide import QtCore, QtGui

from maverig.data import dataHandler
from maverig.utils import tableWidgets

regexp_name = QtCore.QRegExp('^[\w]+$')
regexp_sim_and_model = QtCore.QRegExp('^[\w]{2,}(-\w*)?$')
regexp_caption = QtCore.QRegExp('^.+$')
regexp_address = QtCore.QRegExp('^.+$')


def is_acceptable(l_edit):
    return l_edit.validator().validate(l_edit.text(), 0)[0] == QtGui.QValidator.Acceptable


class ComponentWizardView(QtGui.QWizard):
    def __init__(self, pres, parent=None):
        super(ComponentWizardView, self).__init__(parent)

        self.intro_page = IntroPage(pres)
        self.attribute_parameter_page = AttributeParameterPage(pres, self)

        self.addPage(self.intro_page)
        self.addPage(self.attribute_parameter_page)
        self.addPage(ConclusionPage())

        self.associated_presenter = pres
        self.setWindowTitle(_("Component Wizard"))
        self.setModal(True)
        self.show()

    def closeEvent(self, event):
        self.associated_presenter.on_close_wizard()

    def init_new_simulator_gui(self):
        """initializes the dialog to add a new simulator"""
        cancel_button = self.button(QtGui.QWizard.CancelButton)
        cancel_button.clicked.connect(self.associated_presenter.on_close_wizard)

        self.name_ok = False
        self.adress_ok = False

        self.new_simulator_dialog = QtGui.QDialog()
        self.new_simulator_dialog.setWindowTitle(_("Add new simulator"))

        self.simulator_grid = QtGui.QGridLayout()

        self.button_simulator_add = QtGui.QPushButton(_("Add"))
        self.button_simulator_add.clicked.connect(self.associated_presenter.on_add_simulator_triggered)
        self.button_simulator_cancel = QtGui.QPushButton(_("Cancel"))
        self.button_simulator_cancel.clicked.connect(self.new_simulator_dialog.close)

        string_new_simulator = _("Define the new simulator")
        self.simulator_grid.addWidget(QtGui.QLabel("<p><b>{}</b></p>".format(string_new_simulator)), 0, 0)

        self.simulator_grid.addWidget(QtGui.QLabel(_("Name")), 1, 0)
        self.l_edit_simulator_name = QtGui.QLineEdit()
        self.l_edit_simulator_name.setAccessibleName("name_access")
        validator__simulator_name = QtGui.QRegExpValidator(regexp_sim_and_model)
        self.l_edit_simulator_name.setValidator(validator__simulator_name)
        self.l_edit_simulator_name.textChanged.connect(self.check_state)
        self.l_edit_simulator_name.textChanged.emit(self.l_edit_simulator_name.text())
        self.l_edit_simulator_name.setToolTip(_("Name of the new simulator"))
        self.simulator_grid.addWidget(self.l_edit_simulator_name, 1, 1)

        self.simulator_grid.addWidget(QtGui.QLabel(_("Starter")), 2, 0)
        self.c_box_simulator_starter = QtGui.QComboBox()
        self.c_box_simulator_starter.setToolTip(_("Choose how to start the simulator"))
        self.c_box_simulator_starter.addItem(("python"))
        self.c_box_simulator_starter.addItem(("cmd"))
        self.c_box_simulator_starter.addItem(("connect"))
        self.simulator_grid.addWidget(self.c_box_simulator_starter, 2, 1)

        self.simulator_grid.addWidget(QtGui.QLabel(_("Address")), 3, 0)
        self.l_edit_simulator_address = QtGui.QLineEdit()
        self.l_edit_simulator_address.setAccessibleName("adress_access")
        validator_name = QtGui.QRegExpValidator(regexp_address)
        self.l_edit_simulator_address.setValidator(validator_name)
        self.l_edit_simulator_address.textChanged.connect(self.check_state)
        self.l_edit_simulator_address.textChanged.emit(self.l_edit_simulator_address.text())
        self.l_edit_simulator_address.setToolTip(_("Address of the new simulator"))
        self.simulator_grid.addWidget(self.l_edit_simulator_address, 3, 1)

        self.simulator_grid.addWidget(QtGui.QLabel(_("Parameters")), 4, 0)
        self.table_simulator_params = tableWidgets.AutoRowTableWidget()
        self.table_simulator_params.setColumnCount(2)
        self.table_simulator_params.setEditTriggers(QtGui.QTableWidget.AllEditTriggers)
        self.table_simulator_params.setHorizontalHeaderLabels([_("Parameter"), _("Default Value")])
        self.table_simulator_params.setVerticalScrollMode(QtGui.QTableWidget.ScrollPerPixel)
        self.table_simulator_params.verticalHeader().hide()
        self.table_simulator_params.append_row()
        self.table_simulator_params.horizontalHeader().setStretchLastSection(True)
        self.table_simulator_params.setToolTip(_("Specify which parameters are needed by this simulator. "
                                                "When starting a simulator, equally named "
                                                "component parameters will replace specified default values."))
        self.simulator_grid.addWidget(self.table_simulator_params, 4, 1)

        self.simulator_grid.addWidget(QtGui.QLabel("<br><br>"), 5, 0)

        self.simulator_grid.addWidget(self.button_simulator_add, 6, 0)
        self.simulator_grid.addWidget(self.button_simulator_cancel, 6, 1)

        self.new_simulator_dialog.setLayout(self.simulator_grid)
        self.new_simulator_dialog.exec_()

    def accept(self):
        self.associated_presenter.on_add_component()

    def reject(self):
        super().reject()
        self.associated_presenter.on_close_wizard()

    def simulator_update(self):
        self.intro_page.simulator_update()

    def icon_update(self):
        self.intro_page.icon_update()

    def check_state(self):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b'  # green
            if sender.accessibleName() == "adress_access":
                self.adress_ok = True
            if sender.accessibleName() == "name_access":
                self.name_ok = True
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
            if sender.accessibleName() == "adress_access":
                self.adress_ok = False
            if sender.accessibleName() == "name_access":
                self.name_ok = False
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
        if self.adress_ok and self.name_ok:
            self.button_simulator_add.setEnabled(True)
        else:
            self.button_simulator_add.setEnabled(False)


class IntroPage(QtGui.QWizardPage):
    """initializes the first dialog to add general component information"""

    def __init__(self, pres, parent=None):
        super(IntroPage, self).__init__(parent)

        self.associated_presenter = pres
        self.setTitle(_("Component type"))
        string_gen_comp = _("Define the general component information and settings")
        self.setSubTitle("{}<br>".format(string_gen_comp))
        self.grid = QtGui.QGridLayout()
        # self.associated_presenter = pres
        # self.associated_presenter.init_view(self)
        string_new_component = _("Describe the new component")
        self.grid.addWidget(QtGui.QLabel("<p><b>{}</b></p>".format(string_new_component)), 0, 0)

        self.grid.addWidget(QtGui.QLabel(("Simulator")), 1, 0)
        self.c_box_simulator = QtGui.QComboBox()
        self.c_box_simulator.setToolTip(("Choose the simulator"))
        self.grid.addWidget(self.c_box_simulator, 1, 1)
        self.simulator_update()

        self.button_new_simulator = QtGui.QPushButton(("+"))
        self.button_new_simulator.setFixedSize(20, 20)
        self.button_new_simulator.clicked.connect(self.associated_presenter.on_new_simulator_triggered)
        self.grid.addWidget(self.button_new_simulator, 1, 2)

        self.grid.addWidget(QtGui.QLabel(_("Model")), 2, 0)
        self.l_edit_name = QtGui.QLineEdit()
        validator_name = QtGui.QRegExpValidator(regexp_sim_and_model)
        self.l_edit_name.setValidator(validator_name)
        self.l_edit_name.textChanged.connect(self.check_state)
        self.l_edit_name.textChanged.connect(self.completeChanged)
        self.l_edit_name.textChanged.emit(self.l_edit_name.text())
        self.l_edit_name.setToolTip(_("Mosaik model and optional suffixed name separated by '-'."))
        self.grid.addWidget(self.l_edit_name, 2, 1)

        self.grid.addWidget(QtGui.QLabel(_("Icon")), 3, 0)
        self.c_box_icon = ComboUpdatingBox()
        self.c_box_icon.popup_triggered.connect(self.icon_update)
        self.c_box_icon.setToolTip(_("Define the icon"))
        self.c_box_icon.setIconSize(QtCore.QSize(30, 30))
        self.grid.addWidget(self.c_box_icon, 3, 1)
        self.icon_update()

        self.button_new_icon = QtGui.QPushButton(("+"))
        self.button_new_icon.setToolTip(_("Add a new icon"))
        self.button_new_icon.setFixedSize(20, 20)
        self.button_new_icon.clicked.connect(lambda: self.add_new_icon())
        self.grid.addWidget(self.button_new_icon, 3, 2)

        self.grid.addWidget(QtGui.QLabel(_("Drawing mode")), 4, 0)
        self.c_box_drawing = QtGui.QComboBox()
        self.c_box_drawing.setToolTip(_("Define the drawing mode"))
        self.c_box_drawing.addItems(['icon', 'line-icon-line', 'line', 'node'])
        self.grid.addWidget(self.c_box_drawing, 4, 1)

        self.grid.addWidget(QtGui.QLabel(_("Category")), 5, 0)
        self.c_box_category = QtGui.QComboBox()
        self.c_box_category.setToolTip(_("Choose the category"))
        self.grid.addWidget(self.c_box_category, 5, 1)
        self.category_update()

        self.button_new_category = QtGui.QPushButton(("+"))
        self.button_new_category.setToolTip(_("Create a new category"))
        self.button_new_category.setFixedSize(20, 20)
        self.button_new_category.clicked.connect(lambda: self.new_category_dialog())
        self.grid.addWidget(self.button_new_category, 5, 2)

        self.grid.addWidget(QtGui.QLabel(_("Tooltip")), 6, 0)
        self.l_edit_desc = QtGui.QLineEdit()
        self.l_edit_desc.setToolTip(_("Tooltip of the new component"))
        self.grid.addWidget(self.l_edit_desc, 6, 1)

        self.grid.addWidget(QtGui.QLabel("<br><br>"), 8, 0)

        self.setLayout(self.grid)

    @QtCore.Slot(int)
    def icon_update(self, index=None):
        self.c_box_icon.clear()
        dirs = os.listdir(dataHandler.get_normpath("maverig/data/components/icons/"))
        for file in dirs:
            norm_path = dataHandler.get_component_icon(file)
            if file and os.path.isfile(norm_path):
                self.c_box_icon.addItem(QtGui.QIcon(norm_path), "", os.path.basename(file))
        if index and self.c_box_icon.count() > index:
            self.c_box_icon.setCurrentIndex(index)

    def add_new_icon(self):
        path, filter = QtGui.QFileDialog.getOpenFileName(self, _("Add new Icon"),
                                                         "", _("Images") + " (*.svg *.png *.jpg)")
        if path:
            pieces_of_path = path.split("/")
            name = pieces_of_path[-1]
            shutil.copyfile(path, dataHandler.get_component_icon(name))
            self.c_box_icon.addItem(QtGui.QIcon(dataHandler.get_component_icon(name)), "", name)
            self.c_box_icon.setCurrentIndex(self.c_box_icon.findData(name))

    def simulator_update(self):
        self.c_box_simulator.clear()
        simulator_names = self.associated_presenter.get_simulator_names()
        for name in simulator_names:
            self.c_box_simulator.addItem(name)

    def category_update(self):
        self.c_box_category.clear()
        category_names = self.associated_presenter.get_category_names()
        for name in category_names:
            self.c_box_category.addItem(name)

    def new_category_dialog(self):
        """Open a dialog to enter the new for a new component category."""
        text, ok = QtGui.QInputDialog.getText(self, _("Input Dialog"),
                                              _("Enter the new category name:"))
        test_text = re.match("^[a-zA-Z0-9_.-" "]+$", str(text))
        if ok and test_text is not None:
            self.c_box_category.addItem((str(text)))
            self.c_box_category.setCurrentIndex(self.c_box_category.findText(str(text)))

    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def isComplete(self):
        return is_acceptable(self.l_edit_name)


class AttributeParameterPage(QtGui.QWizardPage, QtGui.QWizard):

    def __init__(self, pres, view, parent=None):
        super(AttributeParameterPage, self).__init__(parent)

        self.associated_presenter = pres

        self.setTitle(_("Parameter and attributes"))
        string_specify = _("Specify attributes and parameters for the component.")
        self.setSubTitle("{}<br>".format(string_specify))

        self.simulator_grid = QtGui.QGridLayout()
        string_comp_params = _("Define the component parameters")
        self.simulator_grid.addWidget(QtGui.QLabel("<p><b>{}</b></p>".format(string_comp_params)), 0, 0)

        self.param_tabs = Tabs(self.add_new_parameter_tab)
        self.add_new_parameter_tab()
        self.simulator_grid.addWidget(self.param_tabs, 1, 0)

        self.simulator_grid.addWidget(QtGui.QLabel("<br><br>"), 2, 0)

        string_comp_attrs = _("Define the component attributes")
        self.simulator_grid.addWidget(QtGui.QLabel("<p><b>{}</b></p>".format(string_comp_attrs)), 3, 0)

        self.attr_tabs = Tabs(self.add_new_attribute_tab)
        self.add_new_attribute_tab()
        self.simulator_grid.addWidget(self.attr_tabs, 4, 0)

        self.simulator_grid.addWidget(QtGui.QLabel("<br><br>"), 5, 0)

        self.setLayout(self.simulator_grid)

    def add_new_parameter_tab(self):
        """If the button in the corner of the tab container is pushed there has to be a new tab for
        an individual parameter"""
        tab = ParameterTab()
        tabs = self.param_tabs
        tabs.setCurrentIndex(tabs.addTab(tab, ""))

        tab.state_checked.connect(self.completeChanged)

        # automatically set tab label to text of name
        tab.l_edit_parameter_name.textChanged.connect(lambda text: tabs.setTabText(tabs.indexOf(tab), text))

    def add_new_attribute_tab(self):
        """If the button in the corner of the tab container is pushed there has to be a new tab for
        an individual attribute"""
        tab = AttributeTab()
        tabs = self.attr_tabs
        tabs.setCurrentIndex(tabs.addTab(tab, ""))

        tab.state_checked.connect(self.completeChanged)

        # automatically set tab label to text of name
        tab.l_edit_attribute_name.textChanged.connect(lambda text: tabs.setTabText(tabs.indexOf(tab), text))

    def isComplete(self):
        # TODO: HGU - better error handling
        return all([self.param_tabs.widget(i).is_ok() for i in range(self.param_tabs.count())]) and \
            all([self.attr_tabs.widget(i).is_ok() for i in range(self.attr_tabs.count())])


class ConclusionPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(ConclusionPage, self).__init__(parent)

        self.setTitle(_("Conclusion"))
        self.setPixmap(QtGui.QWizard.WatermarkPixmap,
                       QtGui.QPixmap(':/images/watermark2.png'))

        self.label = QtGui.QLabel()
        self.label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def initializePage(self):
        finishText = self.wizard().buttonText(QtGui.QWizard.FinishButton)
        finishText = finishText.replace('&', '')
        self.label.setText(_("Click %s to create the component.") % finishText)


class Tabs(QtGui.QTabWidget):

    def __init__(self, tab_factory_method):
        """A tab container widget which can add and remove tabs, but keeps at least one tab.
        Tabs are created with ``tab_factory_method()``."""
        super().__init__()
        self.tabCloseRequested.connect(self.removeTab)
        self.setTabsClosable(False)
        self.setMovable(True)

        self.add_tab_button = QtGui.QPushButton("+")
        self.add_tab_button.setFixedWidth(20)
        self.add_tab_button.clicked.connect(tab_factory_method)
        self.setCornerWidget(self.add_tab_button)

    def tabInserted(self, index):
        super().tabInserted(index)
        self.setTabsClosable(self.count() > 1)

    def tabRemoved(self, index):
        super().tabInserted(index)
        self.setTabsClosable(self.count() > 1)


class ParameterTab(QtGui.QWidget):

    state_checked = QtCore.Signal()

    def __init__(self):
        """Initialize an attribute tab."""
        super(ParameterTab, self).__init__()

        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(QtGui.QLabel(_("Name")), 1, 0)
        self.l_edit_parameter_name = QtGui.QLineEdit()
        validator_name = QtGui.QRegExpValidator(regexp_name)
        self.l_edit_parameter_name.setValidator(validator_name)
        self.l_edit_parameter_name.textChanged.connect(self.check_state)
        self.l_edit_parameter_name.setToolTip(_("Name of the new parameter"))
        self.grid.addWidget(self.l_edit_parameter_name, 1, 1)

        self.grid.addWidget(QtGui.QLabel(_("Caption")), 2, 0)
        self.l_edit_parameter_caption = QtGui.QLineEdit()
        validator_parameter_caption = QtGui.QRegExpValidator(regexp_caption)
        self.l_edit_parameter_caption.setValidator(validator_parameter_caption)
        self.l_edit_parameter_caption.textChanged.connect(self.check_state)
        self.l_edit_parameter_caption.setToolTip(_("Caption of the new parameter"))
        self.grid.addWidget(self.l_edit_parameter_caption, 2, 1)

        self.grid.addWidget(QtGui.QLabel(_("Datatype")), 3, 0)
        self.c_box_parameter_datatype = QtGui.QComboBox()
        self.c_box_parameter_datatype.setToolTip(_("Datatype of the new parameter"))
        self.c_box_parameter_datatype.addItems(['float', 'int', 'bool', 'string', 'file (*.csv)'])
        self.grid.addWidget(self.c_box_parameter_datatype, 3, 1)

        self.grid.addWidget(QtGui.QLabel(_("Accepted values")), 4, 0)
        self.table_parameter_accepted = tableWidgets.AutoRowTableWidget()
        self.table_parameter_accepted.setEditTriggers(QtGui.QTableWidget.AllEditTriggers)
        self.table_parameter_accepted.setVerticalScrollMode(QtGui.QTableWidget.ScrollPerPixel)
        self.table_parameter_accepted.horizontalHeader().hide()
        self.table_parameter_accepted.verticalHeader().hide()
        self.table_parameter_accepted.setColumnCount(1)
        self.table_parameter_accepted.append_row()
        self.table_parameter_accepted.horizontalHeader().setStretchLastSection(True)
        self.table_parameter_accepted.setToolTip(_("Accepted values of the new parameter"))
        self.grid.addWidget(self.table_parameter_accepted, 4, 1)

        self.grid.addWidget(QtGui.QLabel(_("Default value")), 5, 0)
        self.l_edit_default = QtGui.QLineEdit()
        self.l_edit_default.setToolTip(_("Insert a value to define the default value"))
        self.grid.addWidget(self.l_edit_default, 5, 1)

    def check_state(self):
        for widget in [self.l_edit_parameter_name, self.l_edit_parameter_caption]:
            state = widget.validator().validate(widget.text(), 0)[0]
            empty = not self.l_edit_parameter_name.text() and not self.l_edit_parameter_caption.text()
            if empty:
                color = None
            elif state == QtGui.QValidator.Acceptable:
                color = '#c4df9b'  # green
            elif state == QtGui.QValidator.Intermediate:
                color = '#fff79a'  # yellow
            else:
                color = '#f6989d'  # red
            widget.setStyleSheet('QLineEdit { background-color: %s }' % color)
        self.state_checked.emit()

    def is_ok(self):
        empty = not self.l_edit_parameter_name.text() and not self.l_edit_parameter_caption.text()
        return empty or (is_acceptable(self.l_edit_parameter_name) and is_acceptable(self.l_edit_parameter_caption))


class AttributeTab(QtGui.QWidget):

    state_checked = QtCore.Signal()

    def __init__(self):
        """Initialize an attribute tab."""
        super(AttributeTab, self).__init__()

        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(QtGui.QLabel(_("Static")), 0, 0)
        self.c_box_static = QtGui.QCheckBox()
        self.c_box_static.setToolTip(_("Choose whether attribute values are static or dynamic"))
        self.grid.addWidget(self.c_box_static, 0, 1)

        self.grid.addWidget(QtGui.QLabel(_("Name")), 1, 0)
        self.l_edit_attribute_name = QtGui.QLineEdit()
        validator_attribute_name = QtGui.QRegExpValidator(regexp_name)
        self.l_edit_attribute_name.setValidator(validator_attribute_name)
        self.l_edit_attribute_name.textChanged.connect(self.check_state)
        self.l_edit_attribute_name.setToolTip(_("Name of the new attribute"))
        self.grid.addWidget(self.l_edit_attribute_name, 1, 1)

        self.grid.addWidget(QtGui.QLabel(_("Caption")), 2, 0)
        self.l_edit_attribute_caption = QtGui.QLineEdit()
        validator_attribute_caption = QtGui.QRegExpValidator(regexp_caption)
        self.l_edit_attribute_caption.setValidator(validator_attribute_caption)
        self.l_edit_attribute_caption.textChanged.connect(self.check_state)
        self.l_edit_attribute_caption.setToolTip(_("Caption of the new attribute"))
        self.grid.addWidget(self.l_edit_attribute_caption, 2, 1)

        self.grid.addWidget(QtGui.QLabel(_("Unit")), 4, 0)
        self.l_edit_attribute_unit = QtGui.QLineEdit()
        self.l_edit_attribute_unit.setAccessibleName("unit_access")
        self.l_edit_attribute_unit.setToolTip(_("Unit of the new attribute"))
        self.grid.addWidget(self.l_edit_attribute_unit, 4, 1)

    def check_state(self):
        for widget in [self.l_edit_attribute_name, self.l_edit_attribute_caption]:
            state = widget.validator().validate(widget.text(), 0)[0]
            empty = not self.l_edit_attribute_name.text() and not self.l_edit_attribute_caption.text()
            if empty:
                color = None
            elif state == QtGui.QValidator.Acceptable:
                color = '#c4df9b'  # green
            elif state == QtGui.QValidator.Intermediate:
                color = '#fff79a'  # yellow
            else:
                color = '#f6989d'  # red
            widget.setStyleSheet('QLineEdit { background-color: %s }' % color)
        self.state_checked.emit()

    def is_ok(self):
        empty = not self.l_edit_attribute_name.text() and not self.l_edit_attribute_caption.text()
        return empty or (is_acceptable(self.l_edit_attribute_name) and is_acceptable(self.l_edit_attribute_caption))


class ComboUpdatingBox(QtGui.QComboBox):
    """A Combo Box which provides a signal to infornm when the popup is shown."""
    popup_triggered = QtCore.Signal(int)

    def __init__(self):
        super(ComboUpdatingBox, self).__init__()

    def showPopup(self):
        """Overrides the shopPopup method to provide update functionality"""
        super().showPopup()
        self.popup_triggered.emit(self.currentIndex())


if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    wizard = ComponentWizardView()
    wizard.show()
    sys.exit(app.exec_())
