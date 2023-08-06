import numpy as np
import bisect
from PySide import QtGui, QtCore, QtSvg
from colormath.color_objects import sRGBColor, LabColor
from colormath import color_conversions, color_diff


def lab_color(color):
    """ convert QColor, tuple, list or numpy-array to LabColor """
    if isinstance(color, QtCore.Qt.GlobalColor):
        color = QtGui.QColor(color)
    if isinstance(color, QtGui.QColor):
        color = color.getRgbF()
    if isinstance(color, (tuple, list, np.ndarray)):
        color = sRGBColor(*color[:3])

    color = color_conversions.convert_color(color, LabColor)
    return color


def q_color(color):
    """ convert tuple, list or numpy-array and QGlobalColor to QColor """
    if isinstance(color, QtCore.Qt.GlobalColor):
        return QtGui.QColor(color)

    if isinstance(color, (tuple, list, np.ndarray)):
        return QtGui.QColor(*color)
    return color


def np_color(color):
    """ convert tuple, list, QGlobalColor and QColor to numpy array """
    if isinstance(color, (QtCore.Qt.GlobalColor, QtGui.QColor)):
        color = QtGui.QColor(color).toTuple()
    return np.array(color)


def color_interp(x, values, colors):
    """ return linear color interpolation of value x within values mapped to colors.
    example:
    #>>> x = 0.09
    #>>> values = [0.05, 0.08, 0.1]
    #>>> colors = [Qt.black, Qt.yellow, Qt.red]
    #>>> return QColor(255, 127, 0) # orange """
    #assert values and len(values) == len(colors)

    if x <= values[0]:
        return q_color(colors[0])
    elif x >= values[-1]:
        return q_color(colors[-1])

    r = bisect.bisect(values, x)
    l = r-1

    r_percent = abs(x - values[r]) / abs(values[r] - values[l])
    l_percent = abs(x - values[l]) / abs(values[r] - values[l])

    return q_color(np_color(colors[r]) * r_percent + np_color(colors[l]) * l_percent)


def get_icon_color(filename):
    """ scan an icon and return the most prevalent color """
    # prepare image
    image = QtGui.QImage(24, 24, QtGui.QImage.Format_ARGB32_Premultiplied)  # 24x24 size for color detection
    image.fill(QtCore.Qt.transparent)
    if filename.endswith('.svg'):
        renderer = QtSvg.QSvgRenderer(filename)
        renderer.render(QtGui.QPainter(image))
    else:
        image.load(filename)

    ncolors = {}  # dict of color -> number of color detection count

    # parse image lines and pixels for color detection
    for y in range(image.height()):
        line_bgra = np.reshape(image.scanLine(y), (image.width(), 4))
        line_colors = [(r, g, b, a) for b, g, r, a in line_bgra]

        for pixel_color in line_colors:
            ncolors[pixel_color] = ncolors.get(pixel_color, 0) + 1  # set color hit count

    foreground = lambda c: int(c[:3] not in [(0, 0, 0), (255, 255, 255)])  # no complete black or white color
    opaque = lambda c: int(c[3] > 0) + int(c[3] == 255)

    # sort: place opaque foreground colors with most hit count first
    color_sort_key = lambda c: (foreground(c) + opaque(c), ncolors[c])
    sorted_colors = sorted(ncolors.keys(), key=color_sort_key, reverse=True)

    if sorted_colors:
        return QtGui.QColor(*sorted_colors[0])


def compare_color(color1, color2):
    """ compare two colors (tuple, QColor or LabColor) with delta_e_cie_2000 human color perception approximation
    return a float value where 2.3 corresponds to a JND (just noticeable difference)
    """
    return color_diff.delta_e_cie2000(lab_color(color1), lab_color(color2))


color_map = {}  # map of a color-tuple to list of related distinct colors
__rel_map_base_color = {}  # map of a color-tuple to a approximately similar color-tuple in color-map


def distinct_colors(base_colors):
    """ return a list of colors where approximately same colors in base_colors are replaced by distinct colors """

    def generate_color_list(bc):
        """ generate distinct colors with same hue from base_color
        ordered by lightness difference to base_color """
        bc = q_color(bc)
        bc_l = bc.lightnessF()
        h = max(bc.hslHueF(), 0)
        if bc.saturationF() < 0.1:
            s = 0
            l_list = [0.2, 0.41, 0.53, 0.65, 0.75]
        else:
            s = 0.75
            l_list = [0.15, 0.27, 0.39, 0.51, 0.63, 0.75]

        l_list.sort(key=lambda a: abs(a-bc_l))  # sort by lightness difference
        return [QtGui.QColor.fromHslF(h, s, l) for l in l_list]

    def mapped_base_color(bc, max_diff_treshold=10):
        """ return the related base_color in color_map which might be slightly different.
        Create a new entry in color_map if no similar color is present
        :param max_diff_treshold: set difference tolerance by max_diff_treshold (0..100) """
        # try direct fetch
        bc = q_color(bc).toTuple()
        if bc in color_map:
            return bc
        if bc in __rel_map_base_color:
            return __rel_map_base_color[bc]

        # try search similar color
        for mbc in color_map:
            if compare_color(mbc, bc) < max_diff_treshold:
                __rel_map_base_color[bc] = mbc
                return mbc

        # create
        color_map[bc] = generate_color_list(bc)
        return bc

    result = []
    color_map_indices = {}

    for base_color in base_colors:
        mbc = mapped_base_color(base_color)

        idx = color_map_indices.get(mbc, 0)
        color_map_indices[mbc] = (idx + 1) % len(color_map[mbc])

        result.append(color_map[mbc][idx])

    return result


def distinct_colors_from_palette(base_colors, palette_colors):

    def simple_color_diff(bc, pc):
        bc = q_color(bc)
        pc = q_color(pc)

        bs = bc.hslSaturationF()
        bh = bc.hueF()
        bl = bc.lightnessF()

        cs = pc.hslSaturationF()
        ch = pc.hueF()
        cl = pc.lightnessF()

        # gray scale -> saturation penalty
        if bs < 0.1:
            return np.interp(cs, [0, 0.1, 0.2, 1], [0, 1, 100, 10000])
        else:
        # color scale:
            hue_diff = min(abs(bh-ch), abs((bh+1)-ch), abs(bh-(ch+1)))
            h_penalty = (hue_diff*10)**2
            s_penalty = np.interp(cs, [0, 0.1, 0.2, 0.3], [100000, 1000, 5, 0])
            l_diff = abs(bl-cl)
            l_penalty = np.interp(cl, [0, 0.1, 0.2, 0.3], [100000, 1000, 5, 0]) + l_diff**2
            return h_penalty + s_penalty + l_penalty

    def nearest_color(bc, pal):
        result = None
        result_diff = float('inf')
        for pc in pal:
            temp_diff = simple_color_diff(bc, pc)
            if temp_diff < result_diff:
                result_diff = temp_diff
                result = pc
        return result

    palette_colors = palette_colors.copy()
    result_colors = []
    for base_color in base_colors:
        palette_color = nearest_color(base_color, palette_colors)
        palette_colors.remove(palette_color)

        result_colors.append(palette_color)

    return result_colors


def palette_tableau10():
    """ tableau-10 color set taken from
    http://tableaufriction.blogspot.ro/2012/11/finally-you-can-use-tableau-data-colors.html """
    color_list = [
        [31, 119, 180],
        [255, 127, 14],
        [44, 160, 44],
        [214, 39, 40],
        [148, 103, 189],
        [140, 86, 75],
        [227, 119, 194],
        [127, 127, 127],
        [188, 189, 34],
        [23, 190, 207]
    ]
    return [QtGui.QColor(*c) for c in color_list]


def palette_iwanthue50():
    """ generated colors with http://tools.medialab.sciences-po.fr/iwanthue/
    settings: H=[0..360]  C=[0.. 2]  L=[0..1.15]
    """
    color_list = [
        [155, 101, 35],
        [179, 128, 230],
        [87, 192, 64],
        [89, 175, 165],
        [223, 71, 113],
        [40, 46, 60],
        [196, 150, 157],
        [53, 107, 49],
        [89, 169, 214],
        [224, 96, 40],
        [73, 93, 139],
        [213, 165, 44],
        [154, 59, 59],
        [153, 172, 104],
        [151, 177, 50],
        [38, 48, 24],
        [109, 138, 217],
        [74, 30, 35],
        [60, 101, 84],
        [200, 160, 110],
        [155, 162, 141],
        [85, 177, 120],
        [119, 116, 39],
        [134, 88, 151],
        [116, 89, 99],
        [211, 80, 151],
        [217, 117, 88],
        [103, 54, 25],
        [225, 112, 207],
        [81, 144, 46],
        [240, 73, 69],
        [87, 53, 92],
        [209, 139, 183],
        [120, 120, 81],
        [136, 163, 178],
        [161, 110, 88],
        [165, 93, 120],
        [164, 156, 207],
        [224, 148, 81],
        [65, 107, 126],
        [170, 75, 35],
        [72, 75, 23],
        [228, 139, 39],
        [224, 134, 128],
        [94, 74, 60],
        [219, 108, 144],
        [137, 49, 78],
        [201, 136, 211],
        [177, 155, 52],
        [224, 85, 84]
    ]
    return [QtGui.QColor(*c) for c in color_list]