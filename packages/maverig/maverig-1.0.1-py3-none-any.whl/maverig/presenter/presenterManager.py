from maverig.presenter import menuBarPresenter, scenarioPanelPresenter, modePanelPresenter, \
    propertyPanelPresenter, consolePanelPresenter, toolbarPresenter, statusBarPresenter, progressPresenter, \
    attributePanelPresenter, settingsPresenter


class PresenterManager():
    def __init__(self, model, cfg):
        self.mode_panel_presenter = modePanelPresenter.ModePanelPresenter(self, model, cfg)
        self.console_panel_presenter = consolePanelPresenter.ConsolePanelPresenter(self, model, cfg)
        self.menu_bar_presenter = menuBarPresenter.MenuBarPresenter(self, model, cfg)
        self.property_panel_presenter = propertyPanelPresenter.PropertyPanelPresenter(self, model, cfg)
        self.scenario_panel_presenter = scenarioPanelPresenter.ScenarioPanelPresenter(self, model, cfg)
        self.status_bar_presenter = statusBarPresenter.StatusBarPresenter(self, model, cfg)
        self.toolbar_presenter = toolbarPresenter.ToolbarPresenter(self, model, cfg)
        self.progress_presenter = progressPresenter.ProgressPresenter(self, model, cfg)
        self.attribute_panel_presenter = attributePanelPresenter.AttributePanelPresenter(self, model, cfg)
        self.settings_presenter = settingsPresenter.SettingsPresenter(self, model, cfg)