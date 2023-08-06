from maverig.presenter.group_presenter.abstractGroupPresenter import AbstractGroupPresenter


class NodeGroupPresenter(AbstractGroupPresenter):
    """Presenter class that acts as the event handler between the view and the model for the node group."""

    def __init__(self, presenter_manager, model, elem_id, cfg):
        """Initializes the node group presenter.
        :type presenter_manager: maverig.presenter.presenterManager.PresenterManager
        :type model: maverig.models.model.Model
        :type cfg: maverig.data.configs.cfg
        """
        super().__init__(presenter_manager, model, elem_id, cfg)

    @property
    def mappings_port_vp(self):
        """Maps the port and the v_point, e.g. {'0': node.vp_center}."""
        return {'0': self.view.node.vp_center}