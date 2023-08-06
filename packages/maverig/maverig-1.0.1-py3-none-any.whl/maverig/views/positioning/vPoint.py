from functools import partial

from PySide.QtCore import QPointF

from maverig.utils.event import Event
from maverig.views.positioning.section import section_manager
import time


class Changes:
    none = {}
    all = {'applied', 'moved', 'snapped', 'raster_snapped', 'avoid_invalid', 'calculated', 'followed'}
    indirect = {'moved', 'snapped', 'raster_snapped', 'avoid_invalid', 'calculated', 'followed'}


class Change:
    """ Reason for v_point change """
    origin = None
    applied = 'applied'
    moved = 'moved'
    snapped = 'snapped'
    raster_snapped = 'raster_snapped'
    avoid_invalid = 'avoid_invalid'
    calculated = 'calculated'
    followed = 'followed'


class VPoint:
    """ Virtual Point
    See SectionManager documentation for how positioning works."""

    def __init__(self, parent_item=None):
        self.position_changed = Event()
        self.last_positions = []
        self.trigger_section = section_manager.adjust_section

        self.__pos = QPointF()
        self.new_pos = QPointF()
        self.delta = QPointF()

        self.change = None

        self.parent_item = parent_item
        if parent_item:
            parent_item.add_v_point(self)

        self.followers = dict()  # dict from v_point to adjustment method that reacts on self.position_changed

    @property
    def pos(self):
        return self.__pos

    @pos.setter
    def pos(self, value):
        self.set_pos(value, Change.applied)

    def set_pos(self, value, change):
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
        self.set_pos(self.pos + delta, change)

    def follow(self, v_point, trigger_changes=Changes.indirect, result_change=Change.followed, keep_distance=False):
        """ self keeps hold of v_point.
        adjust self when v_point position change applies to trigger.
        self will change it's position with given reason """
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
        if self in v_point.followers:
            v_point.position_changed -= v_point.followers[self]
            del v_point.followers[self]

    def follows(self, v_point):
        return self in v_point.followers

    def fix(self, v_point):
        """ self keeps hold of v_point and vice versa """
        self.follow(v_point, Changes.all, Change.origin)
        v_point.follow(self, Changes.all, Change.origin)

    def unfix(self, v_point):
        self.unfollow(v_point)
        v_point.unfollow(self)

    @property
    def extern_followers(self):
        """ return followed virtual points of other groups """
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