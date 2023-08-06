from maverig.presenter.group_presenter.abstractGroupPresenter import AbstractGroupPresenter


class LineGroupPresenter(AbstractGroupPresenter):
    """Presenter class that acts as the event handler between the view and the model for the line and line icon
    group."""

    @property
    def mappings_port_vp(self):
        """Maps the port and the v_point, e.g. {'0': endpoint_left.vp_center, '1': endpoint_right.vp_center}."""
        return {'0': self.view.endpoint_left.vp_center, '1': self.view.endpoint_right.vp_center}

    def on_param(self):
        elem = self.model.elements[self.elem_id]
        if 'online' in elem['params']:
            online = elem['params']['online']
            if online:
                self.view.line.line_style = 'solid'
                if self.view.line_left is not None and self.view.line_right is not None:
                    self.view.line_left.line_style = 'solid'
                    self.view.line_right.line_style = 'solid'
            else:
                self.view.line.line_style = 'offline'
                if self.view.line_left is not None and self.view.line_right is not None:
                    self.view.line_left.line_style = 'offline'
                    self.view.line_right.line_style = 'offline'
