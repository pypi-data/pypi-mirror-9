import collections

from PySide import QtGui, QtCore

from maverig.views import abstractView
from maverig.data.settings.settings import Settings, SettingTypes
from maverig.data.config import ConfigKeys


class SettingsView(abstractView.AbstractView):
    """Represents the settings dialog."""

    def __init__(self):
        super(SettingsView, self).__init__()
        self.settings = dict()

    def show(self, cfg):
        """Shows a dialog to change the settings"""
        dialog = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        dialog.setWindowTitle(_("Settings"))

        dialog_layout = QtGui.QVBoxLayout()
        tab_bar = QtGui.QTabWidget()

        for tab in Settings.tabs:
            tab_container = QtGui.QWidget()
            tab_layout = QtGui.QVBoxLayout()
            for setting in tab.settings:
                if setting.type == SettingTypes.CHECK_BOX:
                    if setting.input:
                        setting_layout = QtGui.QHBoxLayout()

                        setting.ui_widget = QtGui.QCheckBox(setting.text())
                        setting.ui_widget.setChecked(cfg[tab.key][setting.key])

                        setting.input.ui_widget = QtGui.QLineEdit()
                        setting.input.ui_widget.setText(cfg[tab.key][setting.input.key])

                        setting_layout.addWidget(setting.ui_widget)
                        setting_layout.addWidget(setting.input.ui_widget)
                        tab_layout.addLayout(setting_layout)
                    elif setting.combo_box:
                        setting_layout = QtGui.QHBoxLayout()

                        setting.ui_widget = QtGui.QCheckBox(setting.text())
                        setting.ui_widget.setChecked(cfg[tab.key][setting.key])

                        setting.combo_box.ui_widget = QtGui.QComboBox()
                        self.__fill_combo_box(setting.combo_box.ui_widget, setting.combo_box.values,
                                              cfg[tab.key][setting.combo_box.key])

                        setting_layout.addWidget(setting.ui_widget)
                        setting_layout.addWidget(setting.combo_box.ui_widget)
                        tab_layout.addLayout(setting_layout)
                    else:
                        setting.ui_widget = QtGui.QCheckBox(setting.text())
                        setting.ui_widget.setChecked(cfg[tab.key][setting.key])
                        tab_layout.addWidget(setting.ui_widget)

                elif setting.type == SettingTypes.COMBO_BOX:
                    setting_layout = QtGui.QHBoxLayout()

                    label = QtGui.QLabel(setting.text())

                    setting.ui_widget = QtGui.QComboBox()
                    self.__fill_combo_box(setting.ui_widget, setting.values, cfg[tab.key][setting.key])

                    if setting.key == ConfigKeys.LANGUAGE:
                        setting.ui_widget.currentIndexChanged.connect(self.associated_presenter.on_language_changed)

                    setting_layout.addWidget(label)
                    setting_layout.addWidget(setting.ui_widget)

                    tab_layout.addLayout(setting_layout)

                elif setting.type == SettingTypes.INPUT:
                    setting_layout = QtGui.QHBoxLayout()

                    label = QtGui.QLabel(setting.text())

                    setting.ui_widget = QtGui.QLineEdit()
                    setting.ui_widget.setText(cfg[tab.key][setting.key])

                    setting_layout.addWidget(label)
                    setting_layout.addWidget(setting.ui_widget)

                    tab_layout.addLayout(setting_layout)

            tab_container.setLayout(tab_layout)
            tab_bar.addTab(tab_container, tab.text())

        buttons_layout = QtGui.QHBoxLayout()
        button_save = QtGui.QPushButton(_("Save"))
        button_save.setDefault(True)
        button_save.clicked.connect(dialog.accept)
        button_cancel = QtGui.QPushButton(_("Cancel"))
        button_cancel.clicked.connect(dialog.reject)
        buttons_layout.addWidget(button_save)
        buttons_layout.addWidget(button_cancel)

        dialog_layout.addWidget(tab_bar)
        dialog_layout.addLayout(buttons_layout)
        dialog.setLayout(dialog_layout)

        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.associated_presenter.apply_settings()
        else:
            dialog.destroy()

    @staticmethod
    def __fill_combo_box(cb_widget, values, selected_data):
        for value in values:
            text, data = value if isinstance(value, tuple) else (value, value)
            if isinstance(text, collections.Callable):
                text = text()  # calls text translation method
            cb_widget.addItem(text, data)
        cb_widget.setCurrentIndex(cb_widget.findData(selected_data))