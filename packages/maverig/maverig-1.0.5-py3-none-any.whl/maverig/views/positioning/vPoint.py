from functools import partial

from PySide.QtCore import QPointF

from maverig.utils.event import Event
from maverig.views.positioning.section import section_manager


class Changes:
    none = {}
    all = {'applied', 'moved', 'snapped', 'raster_snapped', 'avoid_invalid', 'calculated', 'followed'}
    indirect = {'moved', 'snapped', 'raster_snapped', 'avoid_invalid', 'calculated', 'followed'}


class Change:
    """Reason for v_point change."""
    origin = None
    applied = 'applied'
    moved = 'moved'
    snapped = 'snapped'
    raster_snapped = 'raster_snapped'
    avoid_invalid = 'avoid_invalid'
    calculated = 'calculated'
    followed = 'followed'


class VPoint:
    """A Virtual Point which represents a position in scenario.

    Each Virtual Point can follow other Virtual Points via event triggers and adjustment functions on specific changes.

    When setting a position, Position Changed Events are fired section by section through stacked layers,
    where each section stands for a different type of position adjustments
    that would conflict each other if they would all run in one section.
    The position gets applied on :attr:`pos` when the internal layer
    :attr:`section_manager.adjust_section` is being exited.
    This is in order to make multiple relative position changes based on the previous position
    without summing up the movements which would result in negative side effects.

    See :class:`maverig.views.positioning.section.SectionManager` documentation for how positioning works in detail."""

    def __init__(self, parent_item=None):
        self.position_changed = Event()
        """The position changed event with current delta (``QtCore.QPointF``), change (:class:`Change`) and
        section (:class:`maverig.views.positioning.section.Section`) as params."""

        self.last_positions = []
        """A list of last valid positions controlled by
        :class:`maverig.presenter.group_presenter.abstractGroupPresenter.AbstractGroupPresenter`
        in order to undo position changes to not allowed positions."""

        self.trigger_section = section_manager.adjust_section
        """The section layer (:class:`maverig.views.positioning.section.Section`)
        on which adjustment to other virtual points movements should be done."""

        self.__pos = QPointF()
        self.new_pos = QPointF()
        """The last proposed new position."""

        self.delta = QPointF()
        """The last proposed position change distance."""

        self.change = None
        """The last proposed :class:`Change` reason of position change."""

        self.parent_item = parent_item
        """The parent :class:`maverig.views.items.abstractItem.AbstractItem` item where this virtual point is added to
         :attr:`AbstractItem.v_points`."""

        if parent_item:
            parent_item.add_v_point(self)

        self.followers = dict()
        """Virtual points that follow this VPoint.
        A dict of virtual point to adjustment method that reacts on :attr:`position_changed` events."""

    @property
    def pos(self):
        """The position of the virtual point.

        Use :meth:`set_pos` if you want to change the position with a specified *change* reason.
        Setting this property will result in a simple :attr:`Change.applied` *change* reason.
        """
        return self.__pos

    @pos.setter
    def pos(self, value):
        self.set_pos(value, Change.applied)

    def set_pos(self, value, change):
        """Set position (``QtCore.QPointF``) with *change* reason."""
        if value != self.new_pos:
            with section_manager.pos_section:  # initiates the section sequence walk through
                for section in section_manager.sections[1:]:  # iterate beginning with adjust_section
                    section.enter_event += self.__on_enter_section
                section_manager.adjust_section.exit_event += self.__on_exit_section

                self.new_pos = value
                self.delta = self.new_pos - self.__pos
                self.change = change

            return True
        return False

    def move_pos(self, delta, change):
        """Move by *delta* (``QtCore.QPointF``) with *change* reason."""
        self.set_pos(self.pos + delta, change)

    def follow(self, v_point, trigger_changes=Changes.indirect, result_change=Change.followed, keep_distance=True):
        """Follow *v_point*.

        Adjust this VPoint when *v_point* position change applies to *trigger_changes*.
        This VPoint will change it's position with the given *result_change* reason.

        Set *keep_distance* to ``False`` if VPoint should only be moved relatively to v_point movements.
        Otherwise distance to v_point is being fixed as ``QtCore.QPointF``-vector from now on.
        """
        follow_delta = self.pos - v_point.pos if keep_distance else None

        adjust_method = partial(self.__adjust,
                                trigger_section=v_point.trigger_section,
                                trigger_changes=trigger_changes,
                                result_change=result_change,
                                follow_delta=follow_delta)

        self.unfollow(v_point)
        v_point.followers[self] = adjust_method
        v_point.position_changed += adjust_method

    def unfollow(self, v_point):
        """Stop following *v_point*."""
        if self in v_point.followers:
            v_point.position_changed -= v_point.followers[self]
            del v_point.followers[self]

    def follows(self, v_point):
        """Return whether this VPoint follows *v_point* when *v_point* moves."""
        return self in v_point.followers

    def fix(self, v_point):
        """Follow v_point and vice versa."""
        self.follow(v_point, Changes.all, Change.origin)
        v_point.follow(self, Changes.all, Change.origin)

    def unfix(self, v_point):
        """Loose any attachments to *v_point* and vice versa."""
        self.unfollow(v_point)
        v_point.unfollow(self)

    @property
    def extern_followers(self):
        """Return a list of virtual points of other groups that follow this VPoint."""
        return [vp for vp in self.followers if vp.parent_item.parent_group != self.parent_item.parent_group]

    def __on_enter_section(self, section):
        section.enter_event -= self.__on_enter_section
        self.position_changed(self, self.delta, self.change, section)

    def __on_exit_section(self, section):
        section.exit_event -= self.__on_exit_section
        if section == section_manager.adjust_section:
            self.__pos = self.new_pos  # apply new position after all position changes and adjustments have been done

    def __adjust(self, vp, delta, change, section, trigger_section, trigger_changes, result_change, follow_delta):
        if section == trigger_section and change in trigger_changes:
            if result_change == Change.origin:
                result_change = change
            if follow_delta is None:
                self.move_pos(delta, result_change)
            else:
                self.set_pos(vp.new_pos + follow_delta, result_change)


class VPMouse(VPoint):
    """ Virtual point representing the mouse position.
    All followers trigger on mouse_section before other following-adjustments, which will be done in adjust_section """

    def __init__(self):
        super().__init__(None)
        self.trigger_section = section_manager.mouse_section