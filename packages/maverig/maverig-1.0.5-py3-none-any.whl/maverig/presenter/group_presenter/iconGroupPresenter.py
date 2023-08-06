from maverig.presenter.group_presenter.abstractGroupPresenter import AbstractGroupPresenter


class IconGroupPresenter(AbstractGroupPresenter):
    """Presenter class that acts as the event handler between the view and the model for the icon group."""

    @property
    def mappings_port_vp(self):
        """Maps the port and the v_point, e.g. {'0': icon.vp_center}."""
        mapping = {'0': self.view.icon.vp_center}
        for port, endpoint in enumerate(self.view.endpoints, start=1):
            mapping[str(port)] = endpoint.vp_center
        return mapping