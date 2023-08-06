import datetime

from PySide import QtCore

from maverig.presenter.group_presenter.abstractGroupPresenter import scene_mapping
from maverig.utils.forceatlas2 import ForceAtlas2
from maverig.views.positioning.vPoint import Change


class ForceEngine:
    def __init__(self, scenario_panel_presenter, model, scene):
        super().__init__()
        self.scenario_panel_presenter = scenario_panel_presenter
        self.model = model

        self.model.force_dragging = True
        self.model.update()

        self.break_iteration = 50
        self.avoid_overlap_iteration = 40

        self.scene = scene

        self.iteration = 0

        self.layouter = ForceAtlas2(model.graph, scale=10, avoidoverlap=False)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_iteration)
        self.timer.start(0)
        self.start_time = datetime.datetime.now()

    def run_iteration(self):
        self.iteration += 1
        if self.iteration == self.avoid_overlap_iteration:
            self.layouter = ForceAtlas2(self.model.graph, scale=10, avoidoverlap=True)

        self.layouter.do_layout()
        self.apply_positions()

        if self.iteration == self.break_iteration:
            self.__on_break_iteration()
            self.timer.stop()

    def __on_break_iteration(self):
        self.model.force_dragging = False
        self.model.update()

    def apply_positions(self):
        """ applies node position movements on mapped virtual points in scene """

        # move virtual points
        for node, data in self.model.graph.nodes(data=True):
            pos = data['pos']
            qpos = QtCore.QPointF(*pos)

            vp = scene_mapping[self.scene][node]
            vp.set_pos(qpos, Change.moved)
