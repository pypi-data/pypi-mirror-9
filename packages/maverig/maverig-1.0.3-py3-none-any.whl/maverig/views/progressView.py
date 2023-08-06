from PySide import QtCore, QtGui

from maverig.views import abstractView
from maverig.data import dataHandler


class ProgressView(QtGui.QWidget, abstractView.AbstractView):
    """Represents the progress bar."""

    def __init__(self):
        super(ProgressView, self).__init__()

        self.header_label = None
        self.btn_trigger_visibility = None
        self.txt_edit_console = None
        self.progress = None
        self.slider = None
        self.time_hbox = None
        self.bar_vbox = None
        self.end_date = None
        self.end_time = None
        self.timelabels = []
        self.actual_date = None
        self.actual_time = None
        self.starttime_vbox = None
        self.endtime_vbox = None

        self.current_time_bar = None
        self.progress_of_simulation = None

    def init_ui(self):
        # main settings of the progress bar
        s_policy_progress_bar = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        s_policy_progress_bar.setHorizontalStretch(0)
        s_policy_progress_bar.setVerticalStretch(0)
        self.setSizePolicy(s_policy_progress_bar)
        self.setStyleSheet("background-color: #f9f9f4;")

        # vertical layout for the panel
        v_box = QtGui.QVBoxLayout()
        v_box.setSpacing(0)
        v_box.setContentsMargins(0, 0, 0, 0)

        # horizontal layout for the header
        header_layout = QtGui.QGridLayout()

        # label for the header
        self.header_label = QtGui.QLabel(_("Progress"))
        self.header_label.setStyleSheet("padding: 0px; color: #fdfdfd;")
        header_layout.addWidget(self.header_label, 0, 0, QtCore.Qt.AlignCenter)

        # button to trigger the visibility of the progress bar
        self.btn_trigger_visibility = QtGui.QPushButton()
        self.btn_trigger_visibility.setStyleSheet("background-color: white; height: 25px; width: 25px; margin-top:-1px")
        self.btn_trigger_visibility.setIcon(QtGui.QIcon(dataHandler.get_icon("console/close_icon_3.png")))
        self.btn_trigger_visibility.clicked.connect(self.associated_presenter.on_change_visibility_triggered)
        header_layout.addWidget(self.btn_trigger_visibility, 0, 0, QtCore.Qt.AlignRight)

        # header
        progress_header = QtGui.QFrame()
        progress_header.setStyleSheet("background: #484848; padding: -5px;")
        progress_header.setLayout(header_layout)
        s_policy_progress_header = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        progress_header.setSizePolicy(s_policy_progress_header)

        v_box.addWidget(progress_header)

        # time labels
        self.time_hbox = QtGui.QHBoxLayout()
        self.bar_vbox = QtGui.QVBoxLayout()
        self.starttime_vbox = QtGui.QVBoxLayout()
        self.endtime_vbox = QtGui.QVBoxLayout()

        # self.actual_time = QtGui.QLabel()
        self.actual_date = QtGui.QPushButton()
        self.actual_date.setText(str(self.associated_presenter.model.sim_start))
        self.actual_date.setFlat(True)
        self.actual_date.setMinimumWidth(100)
        self.actual_date.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;  background-color: none}")
        self.actual_date.clicked.connect(self.associated_presenter.on_change_dateformat)

        self.actual_time = QtGui.QPushButton()
        self.actual_time.setText(str(self.associated_presenter.model.sim_start))
        self.actual_time.setFlat(True)
        self.actual_time.setMinimumWidth(100)
        self.actual_time.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;  background-color: none}")
        self.actual_time.clicked.connect(self.associated_presenter.on_change_dateformat)

        self.end_date = QtGui.QPushButton()
        self.end_date.setFlat(True)
        self.end_date.setMinimumWidth(100)
        self.end_date.setStyleSheet("QPushButton {border-style: outset; border-width: 0px; background-color: none}")
        self.end_date.clicked.connect(self.associated_presenter.on_change_dateformat)

        self.end_time = QtGui.QPushButton()
        self.end_time.setFlat(True)
        self.end_time.setMinimumWidth(100)
        self.end_time.setStyleSheet("QPushButton {border-style: outset; border-width: 0px; background-color: none}")
        self.end_time.clicked.connect(self.associated_presenter.on_change_dateformat)

        # Label for Time Bar
        self.current_time_bar = QtGui.QLabel()
        self.current_time_bar.setText(_("Current time:"))
        self.current_time_bar.setStyleSheet('QLabel {border-style: outset; border-width: 0px;  background-color: none}')

        # Label for Progress Bar
        self.progress_of_simulation = QtGui.QLabel()
        self.progress_of_simulation.setText(_("Progress of calculation:"))
        self.progress_of_simulation.setStyleSheet(
            'QLabel {border-style: outset; border-width: 0px;  background-color: none}')

        # add to time_hbox
        self.starttime_vbox.addWidget(self.actual_date, 0, QtCore.Qt.AlignBottom)
        self.starttime_vbox.addWidget(self.actual_time, 0, QtCore.Qt.AlignTop)
        self.endtime_vbox.addWidget(self.end_date, 0, QtCore.Qt.AlignBottom)
        self.endtime_vbox.addWidget(self.end_time, 0, QtCore.Qt.AlignTop)
        self.time_hbox.addLayout(self.starttime_vbox)
        self.time_hbox.addLayout(self.bar_vbox)
        self.time_hbox.addLayout(self.endtime_vbox)

        v_box.addLayout(self.time_hbox)

        # slider
        self.slider = QtGui.QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setTickPosition(QtGui.QSlider.TicksAbove)
        QtCore.QObject.connect(self.slider, QtCore.SIGNAL("valueChanged(int)"),
                               self.associated_presenter.on_slider_moved)
        self.slider.setStyleSheet("QSlider {background-color: none}")
        self.slider.setMinimum(0)

        # add to bar_vbox
        self.bar_vbox.addWidget(self.current_time_bar, 0, QtCore.Qt.AlignTop)
        self.bar_vbox.addWidget(self.slider)
        self.bar_vbox.addWidget(self.progress_of_simulation, 0, QtCore.Qt.AlignBottom)

        # progress
        self.progress = QtGui.QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""QProgressBar
        {
            border: 1px solid grey;
            height: 2px !important;
        }
        QProgressBar::chunk
        {
            background-color: #0099FF;
        }""")
        self.progress.setFixedHeight(5)
        self.bar_vbox.addWidget(self.progress)

        self.setLayout(v_box)

    def translate(self):
        self.header_label.setText(_("Progress"))
        self.current_time_bar.setText(_("Current time:"))
        self.progress_of_simulation.setText(_("Progress of calculation:"))