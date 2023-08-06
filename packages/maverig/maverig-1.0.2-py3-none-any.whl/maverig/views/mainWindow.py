from PySide import QtCore, QtGui

from maverig.data import config, dataHandler
from maverig.data.config import ConfigKeys
from maverig.views import scenarioPanelView, modePanelView, consolePanelView, menuBarView, propertyPanelView, \
    toolbarView, statusBarView, progressView, attributePanelView, settingsView


class MainWindow(QtGui.QMainWindow):
    """Represents the starting point of the application. All view layouts within 'maverig/views' are linked inside this
    class.
    """

    def __init__(self, cfg):
        super(MainWindow, self).__init__()

        self.cfg = cfg
        self.setObjectName('maverig')

        self.setWindowTitle('maverig %s' % config.VERSION)
        icon = QtGui.QIcon(dataHandler.get_icon('logo/logo_icon.png'))
        self.setWindowIcon(icon)
        self.central_widget = QtGui.QWidget(self)
        self.showMaximized()

        # size
        s_policy_main_window = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        s_policy_main_window.setHorizontalStretch(0)
        s_policy_main_window.setVerticalStretch(0)
        self.central_widget.setSizePolicy(s_policy_main_window)
        self.grid_layout = QtGui.QGridLayout(self.central_widget)
        self.grid_layout.setSpacing(5)

        # layouts
        self.h_layout_main = QtGui.QHBoxLayout()

        # splitter
        self.splitter_main = QtGui.QSplitter()
        self.splitter_main.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_left = QtGui.QSplitter()
        self.splitter_left.setOrientation(QtCore.Qt.Vertical)
        self.splitter_right = QtGui.QSplitter()
        self.splitter_right.setOrientation(QtCore.Qt.Vertical)

        # add menu bar
        self.menu_bar_view = menuBarView.MenuBarView()
        self.setMenuBar(self.menu_bar_view)

        # add tool bar
        self.toolbar_view = toolbarView.ToolbarView()
        self.addToolBar(self.toolbar_view)

        # create settings view
        self.settings_view = settingsView.SettingsView()

        # add component panel, property panel and attribute panel
        self.mode_view = modePanelView.ModePanelView()
        self.property_view = propertyPanelView.PropertyPanelView()
        self.attribute_view = attributePanelView.AttributePanelView()

        self.splitter_left.addWidget(self.mode_view)
        self.splitter_left.addWidget(self.property_view)
        self.splitter_left.addWidget(self.attribute_view)
        self.splitter_main.addWidget(self.splitter_left)

        # add status bar, scenario panel, progress panel and console panel
        self.status_bar_view = statusBarView.StatusBarView()
        self.scenario_view = scenarioPanelView.ScenarioPanelView()
        self.console_view = consolePanelView.ConsolePanelView()
        self.progress_view = progressView.ProgressView()

        self.splitter_right.addWidget(self.status_bar_view)
        self.splitter_right.addWidget(self.scenario_view)
        self.splitter_right.addWidget(self.progress_view)
        self.splitter_right.addWidget(self.console_view)
        self.splitter_main.addWidget(self.splitter_right)

        # add vertical layouts to the upper horizontal layout
        self.h_layout_main.addWidget(self.splitter_main)

        # organize the main vertical layout as a grid to make it resizable
        self.grid_layout.addLayout(self.h_layout_main, 0, 0, 1, 1)
        self.setCentralWidget(self.central_widget)

        # window on top
        self.activateWindow()
        self.restoreState(QtCore.QByteArray.fromBase64(self.cfg[ConfigKeys.UI_STATE][ConfigKeys.MAIN_WINDOW_STATE]))
        self.restoreGeometry(
            QtCore.QByteArray.fromBase64(self.cfg[ConfigKeys.UI_STATE][ConfigKeys.MAIN_WINDOW_GEOMETRY]))
        self.splitter_main.restoreState(
            QtCore.QByteArray.fromBase64(self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_MAIN_STATE]))
        self.splitter_main.restoreGeometry(
            QtCore.QByteArray.fromBase64(self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_MAIN_GEOMETRY]))
        self.splitter_left.restoreState(
            QtCore.QByteArray.fromBase64(self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_LEFT_STATE]))
        self.splitter_left.restoreGeometry(
            QtCore.QByteArray.fromBase64(self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_LEFT_GEOMETRY]))
        self.splitter_right.restoreState(
            QtCore.QByteArray.fromBase64(self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_RIGHT_STATE]))
        self.splitter_right.restoreGeometry(
            QtCore.QByteArray.fromBase64(self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_RIGHT_GEOMETRY]))
        self.raise_()

    def closeEvent(self, event):
        self.cfg = config.read_config()
        main_window_state = self.saveState().toBase64()
        main_window_geometry = self.saveGeometry().toBase64()
        splitter_main_state = self.splitter_main.saveState().toBase64()
        splitter_main_geometry = self.splitter_main.saveGeometry().toBase64()
        splitter_left_state = self.splitter_left.saveState().toBase64()
        splitter_left_geometry = self.splitter_left.saveGeometry().toBase64()
        splitter_right_state = self.splitter_right.saveState().toBase64()
        splitter_right_geometry = self.splitter_right.saveGeometry().toBase64()
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.MAIN_WINDOW_STATE] = str(main_window_state)
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.MAIN_WINDOW_GEOMETRY] = str(main_window_geometry)
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_MAIN_STATE] = str(splitter_main_state)
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_MAIN_GEOMETRY] = str(splitter_main_geometry)
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_LEFT_STATE] = str(splitter_left_state)
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_LEFT_GEOMETRY] = str(splitter_left_geometry)
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_RIGHT_STATE] = str(splitter_right_state)
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.SPLITTER_RIGHT_GEOMETRY] = str(splitter_right_geometry)
        config.write_config(self.cfg)