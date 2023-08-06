import os
import shutil

import dateutil

from maverig.models.model import Mode, ProgramMode
from maverig.presenter import abstractPresenter
from maverig.data import config, dataHandler
from maverig.data.config import ConfigKeys
from maverig.views import componentWizardView
from maverig.presenter import componentWizardPresenter


class ModePanelPresenter(abstractPresenter.AbstractPresenter):
    """Presenter class that acts as the event handler between the view and the model for the mode panel."""

    def __init__(self, presenter_manager, model, cfg):
        """Initializes the mode panel presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super(ModePanelPresenter, self).__init__(presenter_manager, model, cfg)

        self.component_wizard_presenter = None
        self.component_wizard_view = None

        self.model.language_event += self.on_language
        self.model.mode_event += self.on_mode
        self.model.program_mode_event += self.on_program_mode
        self.model.components_event += self.on_components

        self.buttons = {}  # a dict of comp_name to QPushButton
        self.selected_comp = None

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by View --------------------------------------------------------------------------------------

    def on_btn_context_menu(self, event, comp_name):
        """Creates and opens a context menu when the user performs a right mouse click on a component button."""
        if not self.model.selection_dragging:
            default_components_path = dataHandler.get_normpath('maverig/data/components/default_components')
            default_component = os.path.isfile(default_components_path + '/%s.json' % comp_name)

            is_composition = self.model.program_mode == ProgramMode.composition

            context_menu = self.view.create_btn_context_menu()
            self.view.action_delete.setEnabled(is_composition and not default_component)
            self.view.action_hide.setEnabled(is_composition)
            self.view.action_hide.setChecked(
                comp_name in self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS])
            context_menu.popup(event.globalPos())
            self.selected_comp = comp_name

    def on_context_menu(self, event):
        """Creates and opens a context menu when the user performs a right mouse click in the component panel."""
        if not self.model.selection_dragging:
            is_composition = self.model.program_mode == ProgramMode.composition

            context_menu = self.view.create_context_menu()
            self.view.action_show_invisible.setEnabled(is_composition)
            self.view.action_show_invisible.setChecked(
                self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.SHOW_INVISIBLE_COMPONENTS])
            self.view.action_restore_components.setEnabled(is_composition)
            context_menu.popup(event.globalPos())

    def remove_selected_component(self):
        """Removes a component."""
        os.remove(dataHandler.get_normpath('maverig/data/components/%s.json' % self.selected_comp))
        self.model.components = config.read_components()
        self.model.mode_event.demand()
        self.model.update()

    def hide_selected_component(self):
        """Hides a component."""
        invisible_components = self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS]

        if self.selected_comp in invisible_components:
            invisible_components.remove(self.selected_comp)
        else:
            invisible_components.append(self.selected_comp)
        self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS] = invisible_components
        config.write_config(self.cfg)
        self.model.settings_event.demand()
        self.model.components_event.demand()
        self.model.mode_event.demand()
        self.model.update()

    def show_invisible_components(self):
        """Toggles the visibility of hided components in component panel."""
        self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.SHOW_INVISIBLE_COMPONENTS] = \
            not self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.SHOW_INVISIBLE_COMPONENTS]
        config.write_config(self.cfg)
        self.model.settings_event.demand()
        self.model.components_event.demand()
        self.model.mode_event.demand()
        self.model.update()

    def restore_default_components(self):
        """Removes all components from and restores the default components. The list of hided components in the config
        gets cleared."""

        # TODO: info dialog which components will be deleted
        main_path = dataHandler.get_normpath('maverig/data/components')
        default_components_path = dataHandler.get_normpath('maverig/data/components/default_components')

        for file in os.listdir(main_path):
            file_path = os.path.join(main_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except IOError:
                print('No permissions to delete files.')

        for default_file in os.listdir(default_components_path):
            file_path = os.path.join(default_components_path, default_file)
            try:
                if os.path.isfile(file_path):
                    shutil.copy(file_path, main_path)
            except IOError:
                print('Could not copy default component files.')

        self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS] = []
        config.write_config(self.cfg)
        self.model.components = config.read_components()
        self.model.settings_event.demand()
        self.model.mode_event.demand()
        self.model.update()

    def selection_mode_btn_clicked(self):
        """Switches the mode between 'selection mode' and 'component mode' when the selection mode button is clicked."""
        self.model.switch_modes(Mode.selection, Mode.comp)
        self.model.update()

    def hand_mode_btn_clicked(self):
        """Switches the mode between 'hand mode' and 'component mode' when the hand mode button is clicked."""
        self.model.switch_modes(Mode.hand, Mode.comp)
        self.model.update()

    def add_component_btn_clicked(self):
        """Opens the component wizard."""
        self.view.btn_selection_mode.setChecked(False)
        self.view.btn_hand_mode.setChecked(False)
        self.view.unhover_component_button(self.view.btn_hand_mode)
        self.view.unhover_component_button(self.view.btn_selection_mode)
        self.view.hover_component_button(self.view.btn_add_component)
        self.component_wizard_presenter = componentWizardPresenter.ComponentWizardPresenter(self.presenter_manager,
                                                                                            self.model, self.cfg)
        self.component_wizard_view = componentWizardView.ComponentWizardView(self.component_wizard_presenter)
        self.component_wizard_presenter.init_view(self.component_wizard_view)

    def comp_btn_created(self, btn, comp_name):
        """Adds created button to buttons dict."""
        self.buttons[comp_name] = btn

    def comp_btn_clicked(self, btn, comp_name):
        """Switches the mode between 'component mode' and 'selection mode' when a component button is clicked."""
        if self.model.mode != Mode.comp or self.model.comp != comp_name:
            self.model.mode = Mode.comp
        else:
            self.model.mode = Mode.selection
        self.model.comp = comp_name
        self.model.update()

    def drag_started(self, btn, comp_name):
        """Switches the mode to component mode when a component is dragged."""
        self.model.mode = Mode.comp
        self.model.comp = comp_name
        self.model.update()

    def on_change_visibility_triggered(self):
        """Toggles the visibility of the component panel. Saves the visibility state in the config."""
        self.view.setHidden(not self.view.isHidden())
        self.presenter_manager.menu_bar_presenter.view.action_trigger_component_panel.setChecked(
            not self.view.isHidden())
        self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_COMPONENT_PANEL_VISIBLE] = not self.view.isHidden()
        config.write_config(self.cfg)
        self.model.settings_event.demand()
        self.model.update()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Handle events fired by Model -------------------------------------------------------------------------------------

    def on_language(self):
        """Reacts on language changes. Triggers view reinitialization so that the view adopts the chosen language."""
        self.view.init_ui()

    def on_mode(self):
        """Reacts on mode changes. Updates the component buttons accordingly."""
        if self.model.mode == Mode.selection:
            self.view.btn_selection_mode.setChecked(True)
            self.view.hover_component_button(self.view.btn_selection_mode)
            self.view.unhover_component_button(self.view.btn_hand_mode)

        elif self.model.mode == Mode.hand:
            self.view.btn_hand_mode.setChecked(True)
            self.view.hover_component_button(self.view.btn_hand_mode)
            self.view.unhover_component_button(self.view.btn_selection_mode)

        if self.model.comp:
            btn = self.buttons[self.model.comp]
            if self.model.mode == Mode.comp:
                btn.setChecked(True)
                self.view.hover_component_button(btn)
            else:
                btn.setChecked(False)
                self.view.unhover_component_button(btn)

    def on_program_mode(self):
        """Reacts on program mode changes. In the simulation program mode the component panel is hided while the panel
        is displayed in the composition program mode if the user didn't hide it."""
        if self.model.program_mode == ProgramMode.composition:
            self.view.setHidden(not self.cfg[ConfigKeys.UI_STATE][ConfigKeys.IS_COMPONENT_PANEL_VISIBLE])
        elif self.model.program_mode == ProgramMode.simulation:
            self.view.hide()

    def on_components(self):
        """Reacts on component changes. Triggers view reinitialization so that the panel adopts the changes."""
        self.view.init_ui()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Helper -----------------------------------------------------------------------------------------------------------

    def get_published_components(self):
        """Returns a list with comp_name, category, icon and tooltip of every existing component for component
        grid creation."""
        result = []

        comp_creation_time_getter = lambda c: dateutil.parser.parse(self.model.components[c]['creation_time'])
        first_comp = True
        # submit components sorted by creation time
        for comp_name in sorted(self.model.components, key=comp_creation_time_getter):
            show_invisibles = self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.SHOW_INVISIBLE_COMPONENTS]
            transparency = comp_name in self.cfg[ConfigKeys.MODE_PANEL_SETTINGS][ConfigKeys.INVISIBLE_COMPONENTS]
            visible = show_invisibles or not transparency

            if visible:
                comp = self.model.components[comp_name]
                icon_file = dataHandler.get_component_icon(comp['icon'])
                result.append((comp['sim_model'], comp['category'], icon_file, comp['tooltip'], transparency))
                if first_comp:
                    # set first component as default
                    self.model.comp = comp_name
                    first_comp = False

        return result