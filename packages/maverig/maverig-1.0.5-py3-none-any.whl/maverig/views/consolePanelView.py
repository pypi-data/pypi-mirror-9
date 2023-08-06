from PySide import QtCore, QtGui

from maverig.views import abstractView
from maverig.data import dataHandler


class ConsolePanelView(QtGui.QScrollArea, abstractView.AbstractView):
    """Represents console output. Every action triggered by the user is documented in the console output. This helps
    the user to follow his triggered actions.
    """

    def __init__(self):
        super(ConsolePanelView, self).__init__()

        self.btn_trigger_visibility = None
        self.txt_edit_console = None
        self.v_box_console = None

        self.header_layout = None
        self.header_btn_clear = None
        self.header_label = None
        self.console_header = None
        self.pane_vbox = None

    def init_ui(self):
        # main settings of the console panel
        s_policy_console_panel = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        s_policy_console_panel.setHorizontalStretch(0)
        s_policy_console_panel.setVerticalStretch(1)
        self.setSizePolicy(s_policy_console_panel)
        self.setMinimumSize(1, 1)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # label for the header
        self.header_label = QtGui.QLabel(_("Console"))
        self.header_label.setStyleSheet("padding: 0px; color: #fdfdfd;")

        self.header_layout = QtGui.QGridLayout()
        self.header_layout.addWidget(self.header_label, 0, 0, QtCore.Qt.AlignCenter)

        self.header_btn_clear = QtGui.QPushButton()
        self.header_btn_clear.setStyleSheet("background-color: white; height: 25px; width: 25px")
        self.header_btn_clear.setIcon(QtGui.QIcon(dataHandler.get_icon("console/clear_console.png")))
        self.header_btn_clear.clicked.connect(self.associated_presenter.on_console_clear_triggered)
        self.header_layout.addWidget(self.header_btn_clear, 0, 0, QtCore.Qt.AlignLeft)

        # button to trigger the visibility of the console
        self.btn_trigger_visibility = QtGui.QPushButton()
        self.btn_trigger_visibility.setStyleSheet("background-color: white; height: 25px; width: 25px")
        self.btn_trigger_visibility.setIcon(QtGui.QIcon(dataHandler.get_icon("console/close_icon_3.png")))
        self.btn_trigger_visibility.clicked.connect(self.associated_presenter.on_change_visibility_triggered)
        self.header_layout.addWidget(self.btn_trigger_visibility, 0, 0, QtCore.Qt.AlignRight)

        # header
        self.console_header = QtGui.QFrame()
        self.console_header.setStyleSheet("background: #484848; padding: -5px;")
        # horizontal layout for the header
        self.console_header.setLayout(self.header_layout)
        s_policy_console_header = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.console_header.setSizePolicy(s_policy_console_header)

        # vertical layout for the panel
        self.v_box_console = QtGui.QVBoxLayout()
        self.v_box_console.setSpacing(0)
        self.v_box_console.setContentsMargins(0, 0, 0, 0)
        self.v_box_console.addWidget(self.console_header)

        # text edit for the console output
        self.txt_edit_console = QtGui.QTextBrowser()
        self.txt_edit_console.setFrameStyle(QtGui.QFrame.NoFrame)
        self.v_box_console.addWidget(self.txt_edit_console)

        self.pane_vbox = QtGui.QWidget()
        self.pane_vbox.setLayout(self.v_box_console)

        self.setWidget(self.pane_vbox)

    def translate(self):
        self.header_label.setText(_("Console"))