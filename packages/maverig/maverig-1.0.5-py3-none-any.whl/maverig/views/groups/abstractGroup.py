from maverig.views.abstractView import AbstractView
from maverig.utils.event import Event


class AbstractGroup(AbstractView):
    def __init__(self):
        super().__init__()
        self.items = []
        self.position_changed = Event()
        self.mouse_released = Event()

    def init_view(self, scene=None):
        if scene:
            self.add_to_scene(scene)
        self.position_changed += self.associated_presenter.on_position_changed
        self.mouse_released += self.associated_presenter.on_mouse_released

    def add_to_scene(self, scene):
        """ add subitems to scene """
        for item in self.items:
            item.add_to_scene(scene)

    def add_item(self, item):
        self.items.append(item)
        item.position_changed += self.position_changed

    def remove_item(self, item):
        self.items.remove(item)
        item.position_changed -= self.position_changed

    @property
    def selected(self):
        selected_items = [item.selected for item in self.items]
        return any(selected_items)

    @selected.setter
    def selected(self, value):
        if self.selected != value:
            for item in self.items:
                item.selected = value

    @property
    def enabled(self):
        enabled_items = [item.enabled for item in self.items]
        return all(enabled_items)

    @enabled.setter
    def enabled(self, value):
        if self.enabled != value:
            for item in self.items:
                item.enabled = value

    def clear_effects(self):
        for item in self.items:
            item.clear_effects()

    def clear_state_of_charge_effect(self):
        for item in self.items:
            item.clear_state_of_charge_effect()

    def clear_state_of_charge_tip(self):
        for item in self.items:
            item.clear_state_of_charge_tip()

    def clear_state_of_charge_tip_bg(self):
        for item in self.items:
            item.clear_state_of_charge_tip_bg()

    def set_color_effect(self, color, transparency):
        for item in self.items:
            item.set_color_effect(color, transparency)

    def set_shadow_effect(self, color, shadow_faint, offset1, offset2):
        for item in self.items:
            item.set_shadow_effect(color, shadow_faint, offset1, offset2)

    def set_consumer_bar_effect(self, color, pos, width, height):
        for item in self.items:
            item.set_consumer_bar_effect(color, pos, width, height)

    def set_producer_bar_effect(self, color, pos, width, height):
        for item in self.items:
            item.set_producer_bar_effect(color, pos, width, height)

    def set_state_of_charge_bar(self, color, pos, width, height):
        for item in self.items:
            item.set_state_of_charge_bar(color, pos, width, height)

    def set_state_of_charge_tip(self, color, pos, width, height):
        for item in self.items:
            item.set_state_of_charge_tip(color, pos, width, height)

    def set_state_of_charge_tip_bg(self, color, pos, width, height):
        for item in self.items:
            item.set_state_of_charge_tip_bg(color, pos, width, height)

    @property
    def is_under_mouse(self):
        items_under_mouse = [item.is_under_mouse for item in self.items]
        return any(items_under_mouse)

    def remove(self):
        self.position_changed -= self.associated_presenter.on_position_changed
        for item in self.items.copy():
            item.remove()