from maverig.utils.event import Event


class Section:
    """ synchronization of critical sections and automatic walk trough specified section sequences.
    All section participants are notified via events when a section is entered and leaved (exit).

    Sections can either be started directly (run) or be initiated remotely by calling enter and exit. """

    def __init__(self, name, next_sequence=None, called_by_remote=False):
        self.name = name
        self.next_sequence = next_sequence
        self.called_by_remote = called_by_remote

        self.active_calls = 0

        self.enter_event = Event()
        self.exit_event = Event()

    def run(self):
        if not self.called_by_remote:
            self.__enter__()
            self.__exit__()

    def is_running(self):
        return self.active_calls > 0

    def __enter__(self):
        """ first call enters section """
        self.active_calls += 1

        first_call = self.active_calls == 1
        if first_call or not self.called_by_remote:  # allow re-enter for non remote sections
            # print('enter ' + self.name)
            self.enter_event(self)

    def __exit__(self, *args):
        """ last call exits section """
        last_call = self.active_calls == 1
        if last_call:
            # print('exit ' + self.name)
            self.exit_event(self)

        self.active_calls -= 1

        if last_call and self.next_sequence:
            self.next_sequence.run()

    enter = __enter__
    exit = __exit__


class SectionManager:
    """ Holds a section sequence for positioning on internal, items and presenter side

    Sections divide position_changed-Event-Handling into multiple subjected Phases
    which will be handled one after another.

    Position changes made during an "with section_manager.pos_section"-block will only throw events
    after all "pos_section"-blocks have been exited and the next section (mouse_section) has been entered automatically.

    Then all changed virtual points will throw a position_changed_event in __on_enter_section
    with the actual section as parameter which can be checked on Event-Handling.

    Afterwards all changed virtual points will throw a position_changed_events for the next section and so on...

    This is, how positioning works with VPoints and SectionManager:
    1. pos_section:
        in order to set multiple VPoint positions at the same time, use:
        >>> with section_manager.pos_section:
        >>>    v_point1.set_pos(pos1, Change.moved)
        >>>    v_point2.pos = pos2  # Change == Change.applied

        This is equivalent to:
        >>> section_manager.pos_section.enter
        >>> v_point1.set_pos(pos1, Change.moved)
        >>> v_point2.pos = pos2  # Change == Change.applied
        >>> section_manager.pos_section.exit

        one VPoint can simply be set like this:
        >>> v_point.pos = pos  # Change == Change.applied
        In this case, the pos_section enter and exit will be called remotely by VPoint position setter

        During the time window marked by [pos_section.enter .. adjust_section.exit],
        all position changes are applied on old position values in order to prevent side-effects.

    2. mouse_section:
        Mouse section is entered directly after all positioning has been applied on pos_section.
        (VPoint.__on_enter_section)

        All mouse moved virtual points trigger adjustment (trigger_section) on mouse_section.

    3. adjust_section:
        Adjustment section is entered after primary positioning and mouse moved positions.

        VPoint followings and fixings will be applied by handling VPoint.position_changed on previous position changes.

        VPoint.pos calls still return the old position.
        The new set position is saved internally at VPoint.__new_pos
        and will be applied to VPoint.pos after all adjustment changes have been finished.
        (VPoint.__on_exit_section)

    4. item_section:
        Item section is entered after all affected positions and their followings/fixings have been updated.
        All item positions can now be adapted to VPoint positions by registering on VPoint.position_changed event.
        >>> def on_position_changed(self, vp, delta, change, section):
        >>>     if section == section_manager.item_section:
        >>>         self.graphics_item.setPos(self.graphics_item.pos() + delta)

    5. presenter_section:
        Presenter section is entered after all affected item positions have been updated.
        GroupPresenter can now work on the current VPoint and QGraphicsItem positions and e.g. apply custom followings.
        >>> def on_position_changed(self, vp, delta, change, section):
        >>>     if section == section_manager.presenter_section:
        >>>         other_v_point = self.snap_zone_dockable(v_point)  # needs correct QGraphicsItem positions
        >>>         v_point.follow(other_v_point)
        >>>         other_v_point.follow(v_point, [Change.calculated, Change.raster_snapped])

        The Presenter section may also apply new positions which restarts the section sequence from position level.
    """

    def __init__(self):
        self.presenter_section = Section('presenter_section')  # react on position changes in presenter
        self.item_section = Section('item_section', self.presenter_section)  # view-side: setting positions on QT-Items
        self.adjust_section = Section('adjust_section', self.item_section)  # following: position adjustments
        self.mouse_section = Section('mouse_section', self.adjust_section)
        self.pos_section = Section('pos_section', self.mouse_section, called_by_remote=True)  # positioning on set_pos

        self.sections = [self.pos_section, self.mouse_section, self.adjust_section,
                         self.item_section, self.presenter_section]


section_manager = SectionManager()