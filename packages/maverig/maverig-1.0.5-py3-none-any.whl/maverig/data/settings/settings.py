from maverig.data.settings.abstractSettings import Tab, CheckBoxSetting, ComboBoxSetting
from maverig.data.config import ConfigKeys


class SettingTypes():
    COMBO_BOX = "combo_box"
    INPUT = "input"
    CHECK_BOX = "check_box"


class Settings():
    tabs = []

    # general settings
    general_settings_tab = Tab()
    general_settings_tab.text = lambda: _("General")
    general_settings_tab.key = ConfigKeys.GENERAL_SETTINGS

    languages = ComboBoxSetting()
    languages.text = lambda: _("Language")
    languages.type = SettingTypes.COMBO_BOX
    languages.key = ConfigKeys.LANGUAGE
    languages.values = [(lambda: _("English"), "en_EN"),
                        (lambda: _("German"), "de_DE"),
                        (lambda: _("French"), "fr_FR"),
                        (lambda: _("Spanish"), "es_ES")]

    general_settings_tab.settings.append(languages)

    # simulation settings
    simulation_settings_tab = Tab()
    simulation_settings_tab.text = lambda: _("Simulation")
    simulation_settings_tab.key = ConfigKeys.SIMULATION_SETTINGS

    day_night_vis_setting = CheckBoxSetting()
    day_night_vis_setting.text = lambda: _("Enable day and night visualization")
    day_night_vis_setting.type = SettingTypes.CHECK_BOX
    day_night_vis_setting.key = ConfigKeys.IS_DAY_NIGHT_VIS_ENABLED
    simulation_settings_tab.settings.append(day_night_vis_setting)

    # First Checkbox with a Combobox for Branches, Bus and Trafo
    heat_value_effect_setting1 = CheckBoxSetting()
    heat_value_effect_setting1.text = lambda: _("Enable heat value effects for Grid elements")
    heat_value_effect_setting1.type = SettingTypes.CHECK_BOX
    heat_value_effect_setting1.key = ConfigKeys.IS_HEAT_VALUE_EFFECT_FOR_GRIDS_ENABLED

    heat_value_effect_setting1.combo_box = ComboBoxSetting()
    heat_value_effect_setting1.combo_box.type = SettingTypes.COMBO_BOX
    heat_value_effect_setting1.combo_box.key = ConfigKeys.HEAT_VALUE_EFFECT_GRIDS
    heat_value_effect_setting1.combo_box.values = [(lambda: _("Color"), "Color"),
                                                   (lambda: _("Shadow"), "Shadow")]


    simulation_settings_tab.settings.append(heat_value_effect_setting1)

    # Second Checkbox with a Combobox for House and PV
    heat_value_effect_setting2 = CheckBoxSetting()
    heat_value_effect_setting2.text = lambda: _("Enable heat value effects for Consumer, Producer and Prosumer elements")
    heat_value_effect_setting2.type = SettingTypes.CHECK_BOX
    heat_value_effect_setting2.key = ConfigKeys.IS_HEAT_VALUE_EFFECT_FOR_CPP_ENABLED

    heat_value_effect_setting2.combo_box = ComboBoxSetting()
    heat_value_effect_setting2.combo_box.type = SettingTypes.COMBO_BOX
    heat_value_effect_setting2.combo_box.key = ConfigKeys.HEAT_VALUE_EFFECT_CPP
    heat_value_effect_setting2.combo_box.values = [(lambda: _("Bar"), "Bar"),
                                                   (lambda: _("Shadow"), "Shadow"),
                                                   (lambda: _("Transparency"), "Transparency")]

    simulation_settings_tab.settings.append(heat_value_effect_setting2)

    # add tabs
    tabs.append(simulation_settings_tab)
    tabs.append(general_settings_tab)