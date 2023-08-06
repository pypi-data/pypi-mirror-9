from PySide import QtCore, QtGui

from maverig.views import abstractView
from maverig.data import dataHandler


class StatusBarView(QtGui.QScrollArea, abstractView.AbstractView):
    """Represents the status bar."""

    def __init__(self):
        super(StatusBarView, self).__init__()

        self.status_message = None
        self.btn_trigger_visibility = None
        self.layout = None
        self.pane_vbox = None

    def init_ui(self):
        # style
        s_policy_status_bar = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        s_policy_status_bar.setHorizontalStretch(0)
        s_policy_status_bar.setVerticalStretch(1)
        s_policy_status_bar.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(s_policy_status_bar)
        self.setMinimumSize(1, 1)
        self.setMaximumHeight(25)
        self.setWidgetResizable(True)

        self.layout = QtGui.QGridLayout()

        self.status_message = QtGui.QLabel(_("Start creating your scene!"))
        self.status_message.setStyleSheet("color:#fff; padding-left: 0px;")
        self.layout.addWidget(self.status_message, 0, 0, QtCore.Qt.AlignLeft)

        # button to trigger the visibility
        self.btn_trigger_visibility = QtGui.QPushButton()
        self.btn_trigger_visibility.setStyleSheet(
            "background-color: white; padding-left: -5px; margin-right: 5px; height: 25px; width: 25px; margin-top:-1px")
        self.btn_trigger_visibility.setIcon(QtGui.QIcon(dataHandler.get_icon("console/close_icon_3.png")))
        self.btn_trigger_visibility.clicked.connect(self.associated_presenter.on_change_visibility_triggered)
        self.layout.addWidget(self.btn_trigger_visibility, 0, 0, QtCore.Qt.AlignRight)

        self.pane_vbox = QtGui.QFrame()
        self.pane_vbox.setStyleSheet("padding-left: 5px")
        self.pane_vbox.setLayout(self.layout)

        self.setWidget(self.pane_vbox)


