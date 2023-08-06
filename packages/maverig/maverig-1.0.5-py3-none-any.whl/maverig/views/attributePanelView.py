from functools import partial

from PySide import QtCore, QtGui
from PySide.QtGui import QLabel, QFont
from PySide.QtCore import Qt
import matplotlib

from maverig.data import dataHandler
from maverig.utils import numTools
from maverig.views import abstractView
from matplotlib.font_manager import FontProperties

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
from matplotlib import pyplot
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import matplotlib.patches as mpatches


class AttributePanelView(QtGui.QScrollArea, abstractView.AbstractView):
    """Represents the attribute panel."""

    def __init__(self):
        super(AttributePanelView, self).__init__()
        self.root_pane = None
        self.root_layout = None
        self.container_pane = None
        self.container_layout = None
        self.scroll_area = None

        self.unit = "None"

        self.component_header = None
        self.header_layout = None
        self.header_label = None
        self.info_label = None

        self.ax = None

    def init_ui(self):
        """Init the ui structure for the attribute panel."""
        s_policy_comp_panel = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        s_policy_comp_panel.setVerticalStretch(1)
        self.setSizePolicy(s_policy_comp_panel)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # header
        self.header_label = QtGui.QLabel(_("Attributes"))
        self.header_label.setStyleSheet("padding: 0px; color: #fdfdfd")
        self.header_layout = QtGui.QGridLayout()
        self.header_layout.addWidget(self.header_label, 0, QtCore.Qt.AlignLeft)

        #info label
        self.info_label = QtGui.QLabel(_("No same attributes"))
        self.header_label.setStyleSheet("padding: 0px; color: #fdfdfd")


        # close button
        btn_hide = QtGui.QPushButton()
        btn_hide.setStyleSheet("background-color: white; height: 25px; width: 25px; margin-top:-1px")
        btn_hide.setIcon(QtGui.QIcon(dataHandler.get_icon("console/close_icon_3.png")))
        btn_hide.clicked.connect(self.associated_presenter.on_change_visibility_triggered)
        self.header_layout.addWidget(btn_hide, 0, QtCore.Qt.AlignVCenter, QtCore.Qt.AlignRight)

        self.component_header = QtGui.QFrame()
        self.component_header.setStyleSheet("background: #484848; padding: -5px")
        self.component_header.setLayout(self.header_layout)
        s_policy_component_header = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.component_header.setSizePolicy(s_policy_component_header)

        self.create_attribute_panel()

    def create_attribute_panel(self):
        """Initially create the container layout of the attribute panel."""
        self.container_layout = QtGui.QGridLayout()
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.addWidget(self.info_label)
        self.info_label.setVisible(False)

        self.container_pane = QtGui.QWidget()
        self.container_pane.setLayout(self.container_layout)

        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setFrameStyle(QtGui.QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.container_pane)

        self.root_layout = QtGui.QVBoxLayout()
        self.root_layout.setSpacing(0)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.addWidget(self.component_header)
        self.root_layout.addWidget(self.scroll_area)
        self.root_layout.setAlignment(QtCore.Qt.AlignTop)

        self.root_pane = QtGui.QWidget()
        self.root_pane.setLayout(self.root_layout)
        self.setWidget(self.root_pane)

    def create_attribute_cell(self, name, caption, unit, step_size, lines_labels, lines_values, lines_colors, graph_available):
        """Create an attribute cell for every attribute of a selected element."""
        cell = AttributeCell(name, caption, unit, step_size, lines_labels, lines_values, lines_colors, graph_available, self)
        cell.header_btn_clear.clicked.connect(
            partial(self.associated_presenter.on_change_graph_visibility_triggered, name))
        self.container_layout.addWidget(cell)
        return cell

    def clear_container(self):
        child = self.container_layout.takeAt(0)
        while child is not None and child != 0:
            child.widget().setParent(None)
            del child
            child = self.container_layout.takeAt(0)
        self.container_layout.update()

    def update_info_label(self, value):
        self.info_label.setVisible(value)

    def translate(self):
        self.header_label.setText(_("Attributes"))
        self.info_label.setText(_("No same attributes"))


class AttributeCell(QtGui.QGroupBox, abstractView.AbstractView):
    """Represents one cell which is stored in the container for one attribute."""

    def __init__(self, name, caption, unit, sim_step_size, lines_labels, lines_values, lines_colors, graph_available, view):
        super().__init__()

        self.name = name
        self.caption = caption
        self.unit = unit
        self.step_size = sim_step_size

        # set number of lines to minimum data length
        nlines = min(len(lines_labels), len(lines_values), len(lines_colors))
        self.lines_values = lines_values[:nlines]
        self.lines_colors = lines_colors[:nlines]
        self.lines_labels = lines_labels[:nlines]

        self.graph_available = graph_available
        self.view = view

        self.canvas = None
        self.fig = None
        self.ax = None
        self.legend = None
        self.plot_lines = []

        self.redraw_timer = QtCore.QTimer()
        self.redraw_timer.setSingleShot(True)
        self.redraw_timer.timeout.connect(self.on_draw_graph)

        self.anim = None

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.setFont(font)

        # vertical layout for the panel
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # frame for the header
        frame_header = QtGui.QFrame()
        # padding and setting a fixed max high is critical for mac osx retina visualisation
        frame_header.setStyleSheet("background: #DEDEDE; padding: 0px 0px 0px 0px;")
        # frame_header.setMaximumHeight(30)

        # horizontal layout for the header
        horizontal_header = QtGui.QHBoxLayout()
        frame_header.setLayout(horizontal_header)

        # label for the header
        self.lbl_caption = QLabel(_(caption))
        self.lbl_caption.setStyleSheet("font-weight: bold")
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.lbl_caption.setFont(font)
        horizontal_header.addWidget(self.lbl_caption, 0, QtCore.Qt.AlignLeft)

        self.lbl_value = QLabel()
        self.lbl_value.setStyleSheet("color: black; height: 25px; width: 150px;")
        horizontal_header.addWidget(self.lbl_value, 1, QtCore.Qt.AlignRight)

        # button to trigger the visibility of each Attribute Cell
        self.header_btn_clear = QtGui.QPushButton()
        self.header_btn_clear.setStyleSheet("background-color: #DEDEDE; height: 25px; width: 25px")

        horizontal_header.addWidget(self.header_btn_clear, 0, QtCore.Qt.AlignRight)
        self.header_btn_clear.setVisible(self.graph_available)

        self.layout.addWidget(frame_header)

        if not self.graph_available:
            self.setMaximumHeight(50)

    def __del__(self):
        if self.canvas:
            pyplot.close(self.fig)  # release figure memory

    def translate(self):
        self.lbl_caption.setText(_(self.caption))

    def start_scoll_to_center_anim(self):
        scroll_area = self.view.scroll_area
        scroll_bar = scroll_area.verticalScrollBar()

        center_y = self.pos().y() + 0.5*self.height()
        dest_scroll_y = center_y - 0.5*scroll_area.height()

        self.anim = QtCore.QPropertyAnimation(scroll_bar, 'value')
        self.anim.setDuration(750)
        self.anim.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        self.anim.setStartValue(scroll_bar.value())
        self.anim.setEndValue(dest_scroll_y)
        self.anim.start()

    def set_graph_visibility(self, value):
        if value:
            if self.canvas:
                self.canvas.show()
            else:
                self.create_graph()
            self.header_btn_clear.setIcon(QtGui.QIcon(dataHandler.get_icon("up_arrow.png")))
            self.setMinimumHeight(250)

            self.start_scoll_to_center_anim()
        else:
            if self.canvas:
                self.canvas.hide()
            self.header_btn_clear.setIcon(QtGui.QIcon(dataHandler.get_icon("down_arrow.png")))
            self.setMinimumHeight(50)

    def create_graph(self):
        self.setMinimumHeight(250)
        self.setMaximumHeight(400)
        pyplot.style.use('fivethirtyeight')

        self.fig = pyplot.figure(figsize=(400, 225), dpi=36, facecolor="none", edgecolor="none")
        self.ax = pyplot.subplot(111, axisbg="none", frame_on=False)

        self.ax.grid(axis='y', b=False)  # extra params: linestyle='-', linewidth=1
        self.ax.grid(axis='x', b=False)
        self.ax.xaxis.tick_bottom()
        self.ax.yaxis.tick_left()

        self.ax.tick_params(labelsize=20, colors='0.5', pad=10, direction='out')  # labelbottom='off'

        # zip iterate in order to assert same list lengths
        for values, color in zip(self.lines_values, self.lines_colors):
            self.plot_lines.append(self.ax.plot(values, color=color.name())[0])

        lines_boxes = [mpatches.Patch(color=color.name()) for color in self.lines_colors]

        font_p = FontProperties()
        font_p.set_size('medium')
        self.legend = self.ax.legend(lines_boxes, self.lines_labels, bbox_to_anchor=(0., 1.01, 1., .102),
                                     loc=5, ncol=3, mode="expand", borderaxespad=0, prop=font_p)

        self.ax.set_xlabel(_("Time in minutes"))
        to_minutes = lambda index, pos: int(index*self.step_size)
        self.ax.xaxis.set_major_formatter(pyplot.FuncFormatter(to_minutes))

        if self.unit == "":
            self.ax.set_ylabel(_(self.caption))
        else:
            self.ax.set_ylabel("%s in %s" % (_(self.caption), self.unit))

        # generate the canvas to display the plot
        self.canvas = FigureCanvas(self.fig, self.view.scroll_area)
        self.canvas.setStyleSheet("background-color: rgb(255, 255, 255, 50)")
        # self.canvas.setMinimumHeight(300)

        self.layout.addWidget(self.canvas)

    def resizeEvent(self, event):
        """ adjust graph labels after resize with single shot timer """
        if self.canvas:
            self.redraw_timer.start(100)
        return super().resizeEvent(event)

    def on_draw_graph(self):
        """ auto-adjust padding to lables
        Taken from http://matplotlib.org/faq/howto_faq.html#automatically-make-room-for-tick-labels.
        Workaround for pyplot.tight_layout() due to unpredictable ValueErrors and slowness issues.
        return True if graph has been redrawed on canvas.
        """
        if self.fig.bbox.width * self.fig.bbox.height == 0 or not self.ax.get_renderer_cache():
            return False

        # retrieve maximum text width of y-labels
        left_text_width = max([label.get_window_extent().width for label in self.ax.get_yticklabels()])
        preferred_left = (left_text_width + 20) / self.fig.bbox.width

        # retrieve text height of first x-label
        bottom_text_height = self.ax.get_xticklabels()[0].get_window_extent().height
        preferred_bottom = (bottom_text_height + 20) / self.fig.bbox.height

        # set automatic number and positions of y-ticks according to text- to figure-height ratio
        nbins_max = 15
        nbins_min = 1
        nbins_auto = 0.6 / preferred_bottom
        nbins = max(min(nbins_max, nbins_auto), nbins_min)
        self.ax.yaxis.set_major_locator(pyplot.MaxNLocator(nbins=nbins, steps=[1, 2, 5, 10]))

        # avoid margin crossover, prevent ValueErrors
        preferred_left = min(preferred_left, self.fig.subplotpars.right - 0.2)
        preferred_bottom = min(preferred_bottom, self.fig.subplotpars.top - 0.2)
        # adjust padding if needed
        if abs(self.fig.subplotpars.left - preferred_left) > 0.001 \
                or abs(self.fig.subplotpars.bottom - preferred_bottom) > 0.001:
            self.fig.subplots_adjust(left=preferred_left, bottom=preferred_bottom)

            return self.draw_canvas()

        return False

    def draw_canvas(self):
        """ draw matplotlib graph on canvas.
        return True if drawing has been successful """
        try:
            self.canvas.update()
            self.canvas.flush_events()
            self.canvas.draw()
        except RuntimeError:
            return False
        return True

    def change_content(self, current_value, multivalue, lines_values):
        """Change and update the dynamic content of the attribute cell without recreating the ui."""
        if current_value is None:
            current_value = 'NaN'

        # consider different values when using multiselect
        if multivalue:
            # only valid for one element
            self.lbl_value.setStyleSheet("color: grey")
        else:
            # valid value for all selections
            self.lbl_value.setStyleSheet("color: black")

        value_text = numTools.get_short_value_text(current_value, self.unit)

        if multivalue:
            value_text = '[%s...]' % value_text

        self.lbl_value.setText(value_text)

        if self.canvas:
            self._draw_background()
            self._draw_lines(lines_values)
            self._draw_legend()

            # rescale axis
            self.ax.relim()
            self.ax.autoscale()

            if isinstance(current_value, bool):
                to_bool = lambda x, pos: str(bool(x)) if x in [0, 1] else ""
                self.ax.yaxis.set_major_formatter(pyplot.FuncFormatter(to_bool))

            # SpeedUp matplotlib
            # see "Edit 1" in http://taher-zadeh.com/speeding-matplotlib-plotting-times-real-time-monitoring-purposes/
            self.canvas.update()
            self.canvas.flush_events()
            if not self.on_draw_graph():
                self.draw_canvas()

    def _draw_background(self):

        gridlines = []
        if self.ax.xaxis._gridOnMajor:
            if self.ax.get_frame_on():
                gridlines += self.ax.get_xgridlines()[1:]
            else:
                gridlines += self.ax.get_xgridlines()
        if self.ax.yaxis._gridOnMajor:
            if self.ax.get_frame_on():
                gridlines += self.ax.get_ygridlines()[:-1]
            else:
                gridlines += self.ax.get_ygridlines()

        # temporary redraw background grid in order to prevent flickering
        if self.ax.get_renderer_cache() and gridlines:
            self.ax.draw_artist(self.ax.patch)
            for gridline in gridlines:
                self.ax.draw_artist(gridline)

    def _draw_lines(self, lines_values):
        for plot_line, values in zip(self.plot_lines, lines_values):
            ydata = values
            xdata = range(len(ydata))
            plot_line.set_data(xdata, ydata)
            if self.ax.get_renderer_cache():
                self.ax.draw_artist(plot_line)

    def _draw_legend(self):
        if self.ax.get_renderer_cache():
            if self.legend:
                self.ax.draw_artist(self.legend)


class FigureCanvas(FigureCanvasQTAgg):
    """
    Figure Canvas which holds a graph and redirect scrolling events to a set scroll area.
    """

    def __init__(self, fig, scroll_area):
        super().__init__(fig)
        self.scroll_area = scroll_area

    def wheelEvent(self, event):
        self.scroll_area.wheelEvent(event)

