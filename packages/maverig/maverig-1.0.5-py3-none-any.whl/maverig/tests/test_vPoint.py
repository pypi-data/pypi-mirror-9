from unittest import TestCase

from PySide.QtCore import QPointF

from maverig.views.positioning.vPoint import VPoint, Change


class TestVPoint(TestCase):
    def setUp(self):
        self.vp1 = VPoint()
        self.vp2 = VPoint()

    def test_set_pos(self):
        self.vp1.set_pos(QPointF(1, 1), Change.moved)

        assert self.vp1.pos == QPointF(1, 1)

    def test_move_pos(self):
        self.vp1.pos = QPointF(1, 1)
        self.vp1.move_pos(QPointF(33, 1), Change.applied)

        assert self.vp1.pos == QPointF(33, 1) + QPointF(1, 1)

    def test_follow_follows(self):
        """ self keeps hold of v_point.
        adjust self when v_point position change applies to trigger.
        self will change it's position with given reason """
        self.vp2.follow(self.vp1)
        follower = self.vp2.follows(self.vp1)

        assert follower is True

    def test_unfollow(self):
        self.vp1.follow(self.vp2)
        self.vp1.unfollow(self.vp2)

        assert self.vp1 not in self.vp2.followers

    def test_fix(self):
        """ self keeps hold of v_point and vice versa """
        self.vp2.fix(self.vp1)

        assert self.vp2 in self.vp1.followers and self.vp1 in self.vp2.followers

    def test_unfix(self):
        self.vp2.fix(self.vp1)

        assert self.vp2 in self.vp1.followers and self.vp1 in self.vp2.followers

        self.vp1.unfix(self.vp2)

        assert self.vp2 not in self.vp1.followers and self.vp1 not in self.vp2.followers
