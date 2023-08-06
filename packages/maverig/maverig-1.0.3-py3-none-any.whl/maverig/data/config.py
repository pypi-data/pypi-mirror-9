import polib
import json
import glob
import importlib
from PySide import QtCore
from maverig.data import dataHandler
from maverig.data.settings import defaultSettings

"""Basic application configuration helper methods and constants.

Run this module in order to gather new component description texts
in translation \*.po files under *maverig/data/languages*"""

VERSION = '1.0'


def import_method(module_method_address):
    """Return the python method at the given address.

    *module_method_address* is a string which consists of module address and method name separated by ':'."""
    mod_name, method_name = module_method_address.split(':')
    mod = importlib.import_module(mod_name)
    return getattr(mod, method_name)


def read_components():
    """Return all component descriptions from *maverig/data/components*
    as dict from *sim_model* to component description content"""
    components = {}
    path = dataHandler.get_normpath('maverig/data/components/*.json')
    for filename in glob.glob(path):
        obj = read_json(filename)
        components[obj['sim_model']] = obj
    return components


def read_simulators():
    """Return all simulator descriptions as dict from simulators *name* to simulator description content"""
    simulators = {}
    path = dataHandler.get_normpath('maverig/data/components/simulators/*.json')
    for filename in glob.glob(path):
        obj = read_json(filename)
        simulators[obj['name']] = obj
    return simulators


def read_json(filename):
    """Return the content dict of a \*.json file"""
    with open(filename, "r+") as f:
        obj = json.load(f)
        f.close()
    return obj


def write_json(filename, obj):
    """Write a content dict (*obj*) into a \*.json file"""
    with open(filename, 'w+') as f:
        json.dump(obj, f, indent=4)
        f.close()
    return obj


def read_config():
    """Return the application configuration dict from *maverig/data/cfg.json*"""
    try:
        return read_json(dataHandler.get_config_file('cfg.json'))
    except FileNotFoundError:
        restore_config()
        return read_json(dataHandler.get_config_file('cfg.json'))


def write_config(cfg):
    """Write *cfg* into the configuration file *maverig/data/cfg.json*."""
    write_json(dataHandler.get_config_file('cfg.json'), cfg)


def restore_config():
    """Write the default settings in ``maverig.data.settings.defaultSettings``
    into the configuration file *maverig/data/cfg.json*."""
    write_json(dataHandler.get_config_file('cfg.json'), defaultSettings.default_settings)


class ConfigKeys():
    """Constants with configuration dict keys."""
    # ui state
    UI_STATE = "ui_state"
    MAIN_WINDOW_GEOMETRY = "main_window_geometry"
    MAIN_WINDOW_STATE = "main_window_state"
    SPLITTER_MAIN_GEOMETRY = "splitter_main_geometry"
    SPLITTER_MAIN_STATE = "splitter_main_state"
    SPLITTER_LEFT_GEOMETRY = "splitter_left_geometry"
    SPLITTER_LEFT_STATE = "splitter_left_state"
    SPLITTER_RIGHT_GEOMETRY = "splitter_right_geometry"
    SPLITTER_RIGHT_STATE = "splitter_right_state"
    IS_ATTRIBUTE_PANEL_VISIBLE = "is_attribute_panel_visible"
    IS_COMPONENT_PANEL_VISIBLE = "is_component_panel_visible"
    IS_CONSOLE_PANEL_VISIBLE = "is_console_panel_visible"
    IS_PROGRESS_BAR_VISIBLE = "is_progress_bar_visible"
    IS_PROPERTY_PANEL_VISIBLE = "is_property_panel_visible"
    IS_STATUS_BAR_VISIBLE = "is_status_bar_visible"
    ATTRIBUTE_GRAPHS_VISIBLE = "attribute_graphs_visible"

    # general settings
    GENERAL_SETTINGS = "general_settings"
    LANGUAGE = "language"

    # simulation settings
    SIMULATION_SETTINGS = "simulation_settings"
    IS_DAY_NIGHT_VIS_ENABLED = "is_day_night_vis_enabled"
    IS_HEAT_VALUE_EFFECT_FOR_GRIDS_ENABLED = "is_heat_value_effect_for_grids_enabled"
    IS_HEAT_VALUE_EFFECT_FOR_CPP_ENABLED = "is_heat_value_effect_for_cpp_enabled"
    HEAT_VALUE_EFFECT_GRIDS = "heat_value_effect_grids"
    HEAT_VALUE_EFFECT_CPP = "heat_value_effect_cpp"

    # component panel settings
    MODE_PANEL_SETTINGS = "mode_panel_settings"
    INVISIBLE_COMPONENTS = "invisible_components"
    SHOW_INVISIBLE_COMPONENTS = "show_invisible_components"


""" configuration constants """
SCALE_FACTOR = 1.1
LOWER_SCALE_DISTANCE = 0.6
UPPER_SCALE_DISTANCE = 5.5
RASTER_SIZE = 55


def raster_pos(pos):
    """Return the nearest ``PySide.QtCore.QPointF`` raster coord position to pos."""
    raster_pos_x = round(pos.x() / RASTER_SIZE) * RASTER_SIZE
    raster_pos_y = round(pos.y() / RASTER_SIZE) * RASTER_SIZE
    return QtCore.QPointF(raster_pos_x, raster_pos_y)


""" status messages for displaying in the console view """
ACTIVATED_COMPONENT_MODE = lambda: _("component creation mode")
ACTIVATED_HAND_MODE = lambda: _("hand mode")
ACTIVATED_SELECTION_MODE = lambda: _("selection mode")
ACTIVATED_SIMULATION_MODE = lambda: _("simulation mode")
ACTIVATED_AUTO_LAYOUT_MODE = lambda: _("automatic-layout is active")
SEPARATOR = lambda: ": "
SIMULATION_SPEED = lambda: _("visualisation speed")
SIMULATION_PAUSED = lambda: _("(paused)")

CREATION_INVALID = lambda: _("could not create component - invalid connection")

DOCKING_VALID = lambda: _("valid connection")
LINE_TOO_SHORT = lambda: _("line is too short")
DOCKING_INVALID = lambda: _("invalid connection")
DOCKING_NO_ITEMS = lambda: _("no items to connect to")
ZERO_KM_LENGTH = lambda: _("line length has to be longer than 0 km")

FILE_SAVED = lambda: _(" has been saved successfully.")
FILE_OPENED = lambda: _(" has been loaded successfully.")

MULTI_SELECT_DIFFERENT_VALUES = lambda: _("Notice: Changed values of components that had different values.")

SIMULATION_COMPLETED = lambda: _("Your simulation has completed successfully.")


def create_components_language_po_entries(components=None):
    """Write keys found in components into language \*.po files under *maverig/data/languages*
    in order to simplify the component developers translation process."""
    if not components:
        components = read_components()

    keys = ['caption', 'category', 'tooltip']

    comp_msgids = []
    for comp in components.values():
        comp_msgids += [comp[key] for key in keys if key in comp]
        comp_msgids += [param[key]
                        for param in comp['params'].values()
                        for key in keys if key in param]
        comp_msgids += [attr[key]
                        for attr in comp['attrs'].values()
                        for key in keys if key in attr]

    def unique_list(seq):
        """Fastest way to build ordered list with unique items - see http://stackoverflow.com/a/480227"""
        seen = set()
        return [x for x in seq if not (x in seen or seen.add(x))]

    comp_msgids = unique_list(comp_msgids)

    po_paths = glob.glob(dataHandler.get_normpath('maverig/data/languages/*/LC_MESSAGES/*.po'))
    for po_path in po_paths:
        po = polib.pofile(po_path)

        po_msgids = {e.msgid for e in po} | {""}
        new_msgids = [s for s in comp_msgids if s not in po_msgids]

        for new_msgid in new_msgids:
            po.append(polib.POEntry(msgid=new_msgid))

        if new_msgids:
            po.save()

            print('Created language entries in %s:' % po_path)
            for new_msgid in new_msgids:
                print(' - %s' % new_msgid)

if __name__ == '__main__':
    create_components_language_po_entries()