from maverig.data import config


class AbstractPresenter():
    def __init__(self, presenter_manager, model, cfg=None):
        """ Initializes presenter base class.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        self.model = model
        self.cfg = cfg
        self.view = None
        self.presenter_manager = presenter_manager

        self.model.settings_event += self.on_settings

    def on_settings(self):
        """Reacts on settings respectively config changes."""
        self.cfg = config.read_config()