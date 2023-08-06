import os
import subprocess
import sys

from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from PySide.QtGui import QMessageBox, QSlider

from maverig.data import config
from maverig.data import dataHandler


class SimulationTimeDialog():
    """Represents the simulation time dialog."""

    def __init__(self):
        super(SimulationTimeDialog, self).__init__()
        self.l_speed_value = None

    def show(self, sim_start, sim_end, sim_step_size, vid_speed):
        dialog = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        dialog.setWindowTitle(_("Simulation Time"))

        # add widgets to the dialog
        layout = QtGui.QVBoxLayout()
        l_start = QtGui.QLabel(_("Start Time"))
        l_end = QtGui.QLabel(_("End Time"))  #
        edit_start_time = QtGui.QDateTimeEdit(sim_start)
        edit_end_time = QtGui.QDateTimeEdit(sim_end)
        edit_step_size = QtGui.QLineEdit()
        edit_step_size.setText(str(int(sim_step_size / 60)))  # in minutes
        buttons = QtGui.QHBoxLayout()
        button_save = QtGui.QPushButton(_("Save"))
        button_save.setDefault(True)
        button_save.clicked.connect(dialog.accept)
        button_cancel = QtGui.QPushButton(_("Cancel"))
        button_cancel.clicked.connect(dialog.reject)
        buttons.addWidget(button_save)
        buttons.addWidget(button_cancel)

        vid_speed, vid_speed_rel = self.convert_slider_value_initial(vid_speed)

        l_stepsize = QtGui.QLabel(_("Step Size (in Minutes)"))
        l_speed = QtGui.QLabel(_("Speed"))
        l_speed_slower = QtGui.QLabel(_("Slower"))
        self.l_speed_value = QtGui.QLabel(str(vid_speed_rel))
        self.l_speed_value.setStyleSheet("font-size:9px;")
        self.l_speed_value.setContentsMargins(0, 10, 0, 0)
        l_speed_slower.setAlignment(Qt.AlignLeft)
        l_speed_slower.setStyleSheet("font-size:9px;")
        l_speed_slower.setContentsMargins(0, 10, 0, 0)
        l_speed_faster = QtGui.QLabel(_("Faster"))
        l_speed_faster.setAlignment(Qt.AlignRight)
        l_speed_faster.setStyleSheet("font-size:9px;")
        l_speed_faster.setContentsMargins(0, 10, 0, 0)

        layout.addWidget(l_start)
        layout.addWidget(edit_start_time)
        layout.addWidget(l_end)
        layout.addWidget(edit_end_time)
        layout.addWidget(l_stepsize)
        layout.addWidget(edit_step_size)
        layout.addWidget(l_speed)
        h_description = QtGui.QHBoxLayout()
        h_description.addWidget(l_speed_slower, 0, Qt.AlignLeft)
        h_description.addWidget(self.l_speed_value, 0, Qt.AlignCenter)
        h_description.addWidget(l_speed_faster, 0, Qt.AlignRight)
        layout.addLayout(h_description)
        slider = QSlider()
        slider.setRange(50, 2000)
        slider.setTickInterval(250)
        slider.setSingleStep(250)
        slider.tickInterval()
        slider.setSliderPosition(vid_speed)

        slider.setOrientation(Qt.Horizontal)
        slider.valueChanged.connect(self.convert_slider_value)
        layout.addWidget(slider)

        layout.addLayout(buttons)
        dialog.setLayout(layout)

        # show modal dialog and retrieve data
        if dialog.exec_() == QtGui.QDialog.Accepted:
            new_start_time = edit_start_time.dateTime()
            new_end_time = edit_end_time.dateTime()
            simulation_time = int((new_start_time.secsTo(new_end_time) / 60))  # timespan in minutes
            new_sim_step_size = int(edit_step_size.text())
            new_vid_speed, new_vid_speed_rel = self.convert_slider_value(slider.value())
            if new_start_time >= new_end_time:
                QMessageBox.warning(button_save, _("Warning!!"), _("Start time must be lower than end time"),
                                    buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
                self.show(sim_start, sim_end, sim_step_size, vid_speed)
            elif new_sim_step_size > simulation_time or new_sim_step_size < 1:
                QMessageBox.warning(button_save, _("Warning!!"),
                                    _("Step size must be lower than simulation time or bigger than 0"),
                                    buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
                self.show(sim_start, sim_end, sim_step_size, vid_speed)
            else:
                dialog.destroy()
                return new_start_time, new_end_time, (new_sim_step_size * 60), new_vid_speed, new_vid_speed_rel
        return sim_start, sim_end, sim_step_size, vid_speed, vid_speed_rel

    def convert_slider_value(self, val):
        # convert slider values -
        # 2000 slow and 50 fast
        if 50 <= val < 250:
            speed_rel = 0.5
            val = 2000
        elif 250 <= val < 500:
            speed_rel = 0.625
            val = 1750
        elif 500 <= val < 750:
            speed_rel = 0.75
            val = 1500
        elif 750 <= val < 1000:
            speed_rel = 0.875
            val = 1250
        elif 1000 <= val < 1250:
            speed_rel = 1.0
            val = 1000
        elif 1250 <= val < 1500:
            speed_rel = 1.5
            val = 750
        elif 1500 <= val < 1750:
            speed_rel = 2.0
            val = 500
        elif 1750 <= val < 2000:
            speed_rel = 4.0
            val = 250
        else:
            speed_rel = 8.0
            val = 50

        if self.l_speed_value:
            self.l_speed_value.setText(str(speed_rel))

        return val, speed_rel

    def convert_slider_value_initial(self, val):
        # convert slider values -
        # 2000 slow and 50 fast
        if 50 <= val < 250:
            speed_rel = 8.0
            val = 2000
        elif 250 <= val < 500:
            speed_rel = 4.0
            val = 1750
        elif 500 <= val < 750:
            speed_rel = 2.0
            val = 1500
        elif 750 <= val < 1000:
            speed_rel = 1.5
            val = 1250
        elif 1000 <= val < 1250:
            speed_rel = 1.0
            val = 1000
        elif 1250 <= val < 1500:
            speed_rel = 0.875
            val = 750
        elif 1500 <= val < 1750:
            speed_rel = 0.75
            val = 500
        elif 1750 <= val < 2000:
            speed_rel = 0.625
            val = 250
        else:
            speed_rel = 0.5
            val = 50

        if self.l_speed_value:
            self.l_speed_value.setText(str(speed_rel))

        return val, speed_rel


def go_to_time_dialog(sim_time_instances, sim_index):
    """Shows a dialog to go to an specific simulation time"""

    dialog = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
    dialog.setWindowTitle(_("Go To Specific Simulation Time"))
    label = QtGui.QLabel(_("Go to time: "))

    dialog.setFixedSize(300, 100)

    # add widgets to the dialog
    layout = QtGui.QVBoxLayout()
    time_edit = QtGui.QComboBox()
    for item in sim_time_instances:
        time_edit.addItem(str(item))
    time_edit.setCurrentIndex(sim_index)

    buttons = QtGui.QHBoxLayout()
    button_save = QtGui.QPushButton(_("Save"))
    button_save.setDefault(True)
    button_save.clicked.connect(dialog.accept)
    button_cancel = QtGui.QPushButton(_("Cancel"))
    button_cancel.clicked.connect(dialog.reject)
    buttons.addWidget(button_save)
    buttons.addWidget(button_cancel)

    layout.addWidget(label)
    layout.addWidget(time_edit)
    layout.addLayout(buttons)
    dialog.setLayout(layout)

    if dialog.exec_() == QtGui.QDialog.Accepted:
        return time_edit.currentIndex()
    else:
        dialog.destroy()

    return time_edit.currentIndex()


def inform_dialog():
    msg_box = QMessageBox()
    msg_box.setWindowTitle(_("Warning"))
    msg_box.setText(_("The document has been modified."))
    msg_box.setInformativeText(_("Do you want to save your changes?"))
    msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    for button in msg_box.buttons():
        if msg_box.buttonRole(button) == QMessageBox.AcceptRole:
            button.setText(_("Save"))
        if msg_box.buttonRole(button) == QMessageBox.DestructiveRole:
            button.setText(_("Discard"))
        if msg_box.buttonRole(button) == QMessageBox.RejectRole:
            button.setText(_("Cancel"))
    msg_box.setDefaultButton(QMessageBox.Save)
    return msg_box.exec_()


def error_dialog(title, text, info_text):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setInformativeText(info_text)
    msg_box.addButton("OK", QMessageBox.AcceptRole)
    msg_box.exec_()


def about_dialog():
    dialog = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
    dialog.setWindowTitle(_("About"))
    layout = QtGui.QVBoxLayout()

    image_label = QtGui.QLabel()
    image_label.setAlignment(QtCore.Qt.AlignCenter)
    maverig_logo = dataHandler.get_icon("logo/logo_small.png")
    image_label.setText(
        "<img src=%s></img> <font size=14 color=#484848> %s </font><br>" % (maverig_logo, config.VERSION))

    maverig_text = QtGui.QLabel()
    maverig_text.setAlignment(QtCore.Qt.AlignCenter)
    maverig_text.setText(_("Maverig is a visualization tool based on mosaik <br>"
                           "to compose and simulate smart grid scenarios"))
    copyright_text = QtGui.QLabel()
    copyright_text.setText(" <br><br>Copyright © 2014-2015 Offis<br>")

    buttons = QtGui.QHBoxLayout()
    button_participants = QtGui.QPushButton(_("Participants"))
    button_participants.clicked.connect(participant)
    button_license = QtGui.QPushButton(_("License"))
    button_license.clicked.connect(show_license)
    button_cancel = QtGui.QPushButton(_("Cancel"))
    button_cancel.clicked.connect(dialog.close)

    buttons.addWidget(button_participants)
    buttons.addWidget(button_license)
    buttons.addWidget(button_cancel)

    layout.addWidget(image_label)
    layout.addWidget(maverig_text)
    layout.addWidget(copyright_text)
    layout.addLayout(buttons)

    dialog.setLayout(layout)
    dialog.exec_()


def participant():
    msg_box = QMessageBox()
    msg_box.setWindowTitle(_('Participants'))
    msg_box.setText('<p align="center">'
                    'Hanno G&uuml;nther<br>'
                    'Rouven Pajewski<br>'
                    'Sascha Spengler<br>'
                    'Michael Falk<br>'
                    'Marina Sartison<br>'
                    'Tobias Schwerdtfeger<br>'
                    'Erika Root<br>'
                    'Gerrit Klasen<br>'
                    'Jerome Tammen<br>'
                    'Marius Brinkmann<br>'
                    'Rafael Burschik<br>'
                    'Johary Ny Aina Andrianarisoa Andriamananony'
                    '</p>')
    msg_box.setStandardButtons(QMessageBox.Cancel)
    msg_box.setDefaultButton(QMessageBox.Cancel)
    msg_box.exec_()


def show_license():
    license_path = dataHandler.get_normpath('LICENSE.txt')
    if sys.platform.startswith('darwin'):
        subprocess.call('open', license_path)
    elif os.name == 'nt':
        os.startfile(license_path)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', license_path))


def element_already_exist(string):
    msg_box = QtGui.QMessageBox()
    msg_box.setText(string + " " + _("already exist"))
    msg_box.setInformativeText(_("There is already a component with the same name"))
    msg_box.setStandardButtons(QtGui.QMessageBox.Close)
    msg_box.setIcon(QMessageBox.Information)
    return msg_box