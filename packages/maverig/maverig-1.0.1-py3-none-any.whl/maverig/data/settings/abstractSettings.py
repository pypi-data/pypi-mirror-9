class Tab():
    def __init__(self):
        self.text = None
        self.key = None
        self.settings = []


class Setting():
    def __init__(self):
        self.text = None
        self.type = None
        self.tooltip = None
        self.key = None
        self.ui_widget = None


class CheckBoxSetting(Setting):
    def __init__(self):
        self.input = None
        self.combo_box = None


class InputSetting(Setting):
    def __init__(self):
        self.allowed_values = None


class ComboBoxSetting(Setting):
    def __init__(self):
        self.values = None