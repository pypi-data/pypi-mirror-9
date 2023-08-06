from PySide import QtGui

from maverig.data import dataHandler
from maverig.views import abstractView


class ToolbarView(QtGui.QToolBar, abstractView.AbstractView):
    """Represents the toolbar."""

    def __init__(self):
        super(ToolbarView, self).__init__()

        self.setObjectName("maverig")

        self.action_open = None
        self.action_save = None

        self.action_back_to_start = None
        self.action_reduce_speed = None
        self.action_run = None
        self.action_stop = None
        self.action_increase_speed = None
        self.action_forward_to_end = None

        self.action_zoom_in = None
        self.action_zoom_out = None
        self.action_zoom_fit = None

        self.action_delete = None
        self.action_settings = None

        self.action_auto_layout = None

    def init_ui(self):
        # create actions
        self.action_open = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/fileopen.png')), _('Open'), self)
        self.action_open.setStatusTip(_('Open Scenario'))
        self.action_open.triggered.connect(self.associated_presenter.on_file_open_triggered)

        self.action_save = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/filesave.png')), _('Save'), self)
        self.action_save.setStatusTip(_('Save Scenario'))
        self.action_save.triggered.connect(self.associated_presenter.on_file_save_triggered)

        self.action_back_to_start = QtGui.QAction(
            QtGui.QIcon(dataHandler.get_icon('toolbar/vid_back_to_start.png')),
            _('Back to start'), self)
        self.action_back_to_start.triggered.connect(
            self.associated_presenter.on_back_to_start_triggered)
        self.action_back_to_start.setDisabled(True)

        self.action_reduce_speed = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/vid_back.png')),
                                                 _('Reduce speed'), self)
        self.action_reduce_speed.triggered.connect(self.associated_presenter.on_reduce_speed_triggered)
        self.action_reduce_speed.setDisabled(True)

        self.action_run = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/vid_start.png')),
                                        _('Run'), self)
        self.action_run.triggered.connect(self.associated_presenter.on_run_triggered)

        self.action_stop = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/vid_stop.png')),
                                         _('Stop'), self)
        self.action_stop.triggered.connect(self.associated_presenter.on_stop_triggered)
        self.action_stop.setDisabled(True)

        self.action_increase_speed = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/vid_forward.png')),
                                                   _('Increase speed'), self)
        self.action_increase_speed.triggered.connect(self.associated_presenter.on_increase_speed_triggered)
        self.action_increase_speed.setDisabled(True)

        self.action_forward_to_end = QtGui.QAction(
            QtGui.QIcon(dataHandler.get_icon('toolbar/vid_forward_to_end.png')),
            _('Forward to end'), self)
        self.action_forward_to_end.triggered.connect(
            self.associated_presenter.on_forward_to_end_triggered)
        self.action_forward_to_end.setDisabled(True)

        self.action_zoom_in = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/zoom_in.png')), _('Zoom In'), self)
        self.action_zoom_in.setStatusTip(_('Zoom In'))
        self.action_zoom_in.triggered.connect(self.associated_presenter.on_zoom_in_triggered)

        self.action_zoom_out = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/zoom_out.png')), _('Zoom Out'),
                                             self)
        self.action_zoom_out.setStatusTip(_('Zoom Out'))
        self.action_zoom_out.triggered.connect(self.associated_presenter.on_zoom_out_triggered)

        self.action_zoom_fit = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/zoom_fit.png')), _('Zoom Fit'),
                                             self)
        self.action_zoom_fit.setStatusTip(_('Zoom Fit'))
        self.action_zoom_fit.triggered.connect(self.associated_presenter.on_zoom_fit_triggered)

        self.action_delete = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/delete.png')),
                                           _('Delete Components'), self)
        self.action_delete.setStatusTip(_('Delete Components'))
        self.action_delete.triggered.connect(self.associated_presenter.on_delete_triggered)

        self.action_settings = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/settings.png')), _('Settings'),
                                             self)
        self.action_settings.setStatusTip(_('Settings'))
        self.action_settings.triggered.connect(self.associated_presenter.on_settings_triggered)

        self.action_auto_layout = QtGui.QAction(QtGui.QIcon(dataHandler.get_icon('toolbar/auto_layout.png')),
                                                   _('Auto Layout'), self)
        self.action_auto_layout.setStatusTip(_('Auto Layout'))
        self.action_auto_layout.triggered.connect(self.associated_presenter.on_auto_layout_triggered)

        # add actions to the toolbar
        self.addAction(self.action_open)
        self.addAction(self.action_save)
        self.addSeparator()
        self.addAction(self.action_back_to_start)
        self.addAction(self.action_reduce_speed)
        self.addAction(self.action_run)
        self.addAction(self.action_stop)
        self.addAction(self.action_increase_speed)
        self.addAction(self.action_forward_to_end)
        self.addSeparator()
        self.addAction(self.action_zoom_in)
        self.addAction(self.action_zoom_out)
        self.addAction(self.action_zoom_fit)
        self.addSeparator()
        self.addAction(self.action_delete)
        self.addAction(self.action_settings)
        self.addSeparator()
        self.addAction(self.action_auto_layout)
        self.addSeparator()

        self.setWindowTitle(_('Toolbar'))