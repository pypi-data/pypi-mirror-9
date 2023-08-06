import gettext
import sys
import multiprocessing

from PySide.QtGui import QApplication
from PySide import QtGui

from maverig.utils import logger
from maverig.views import mainWindow
from maverig.models import model
from maverig.presenter import presenterManager
from maverig.data import dataHandler, config
from maverig.data.config import ConfigKeys


class DummyStream():
    """Represents a dummy stream object that overrides the stream objects of sys if application is frozen due to
    compatibility issues on windows."""

    def __init__(self):
        pass

    def write(self, data):
        pass

    def read(self, data):
        pass

    def flush(self):
        pass

    def close(self):
        pass


class EntryPoint():
    """Represents the entry point of the application."""

    def __init__(self):
        # Create models
        self.model = model.Model()

        # Load config
        cfg = config.read_config()

        # Create presenter
        self.presenter_manager = pm = presenterManager.PresenterManager(self.model, cfg)

        # Create views through main window
        self.main_window = mainWindow.MainWindow(cfg)

        # Mapping views
        pm.mode_panel_presenter.view = self.main_window.mode_view
        pm.console_panel_presenter.view = self.main_window.console_view
        pm.menu_bar_presenter.view = self.main_window.menu_bar_view
        pm.property_panel_presenter.view = self.main_window.property_view
        pm.scenario_panel_presenter.view = self.main_window.scenario_view
        pm.status_bar_presenter.view = self.main_window.status_bar_view
        pm.progress_presenter.view = self.main_window.progress_view
        pm.toolbar_presenter.view = self.main_window.toolbar_view
        pm.attribute_panel_presenter.view = self.main_window.attribute_view
        pm.settings_presenter.view = self.main_window.settings_view

        # Mapping presenter
        self.main_window.mode_view.associated_presenter = pm.mode_panel_presenter
        self.main_window.console_view.associated_presenter = pm.console_panel_presenter
        self.main_window.menu_bar_view.associated_presenter = pm.menu_bar_presenter
        self.main_window.property_view.associated_presenter = pm.property_panel_presenter
        self.main_window.scenario_view.associated_presenter = pm.scenario_panel_presenter
        self.main_window.status_bar_view.associated_presenter = pm.status_bar_presenter
        self.main_window.progress_view.associated_presenter = pm.progress_presenter
        self.main_window.toolbar_view.associated_presenter = pm.toolbar_presenter
        self.main_window.attribute_view.associated_presenter = pm.attribute_panel_presenter
        self.main_window.settings_view.associated_presenter = pm.settings_presenter

        # Init view content after mvp mapping is done
        self.main_window.mode_view.init_ui()
        self.main_window.console_view.init_ui()
        self.main_window.menu_bar_view.init_ui()
        self.main_window.property_view.init_ui()
        self.main_window.scenario_view.init_ui()
        self.main_window.status_bar_view.init_ui()
        self.main_window.progress_view.init_ui()
        self.main_window.toolbar_view.init_ui()
        self.main_window.attribute_view.init_ui()

        self.model.update_all()


def main():
    platform = sys.platform
    if platform == 'win32':
        QApplication.setStyle("common")
    if platform == 'linux':
        QApplication.setStyle("cleanlooks")
    if platform == 'darwin':
        QApplication.setStyle("macintosh")
    app = QApplication(sys.argv)
    entry_point = EntryPoint()
    entry_point.main_window.show()
    try:
        sys.exit(app.exec_())
    except (KeyboardInterrupt, SystemExit):
        entry_point.model.simulation.stop()
        raise


if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        logger.activate_logger('maverig-log.txt')
        #sys.__stdout__ = DummyStream()
        #sys.__stderr__ = DummyStream()
        #sys.__stdin__ = DummyStream()
        #sys.stdout = DummyStream()
        #sys.stderr = DummyStream()
        #sys.stdin = DummyStream()
    multiprocessing.freeze_support()
    main()