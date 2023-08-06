from datetime import datetime

from maverig.models.model import ElemPort


__author__ = 'jerometammen'
import sys
from PySide.QtGui import QApplication
from PySide import QtCore, QtGui
from maverig import EntryPoint
from maverig.data import dataHandler


def main():
    platform = sys.platform
    if platform == 'win32':
        QApplication.setStyle("common")
    if platform == 'linux':
        QApplication.setStyle("cleanlooks")
    if platform == 'darwin':
        QApplication.setStyle("macintosh")
    app = QApplication(sys.argv)

    entry_point = EntryPoint.EntryPoint()
    model = entry_point.model

    # #
    #----------------------- Model Initialization --------------------------#
    #                                                                       #

    model.sim_start = datetime(2014, 10, 20, 0, 0, 0)
    model.sim_end = datetime(2014, 10, 24, 23, 59, 59)

    #                                                                       #
    #------------------------------- GRID ----------------------------------#
    #                                                                       #

    #creates refbus
    refbus_1 = model.create_element('PyPower.RefBus', QtCore.QPointF(220, 0))
    model.set_param_value(refbus_1, 'base_kv', 20.00)

    #creates Branch
    branch_1 = model.create_element("PyPower.Branch", QtCore.QPointF())
    model.set_param_value(branch_1, 'btype', 'NA2XS2Y_185')
    model.set_param_value(branch_1, 'online', True)
    model.set_param_value(branch_1, 'l', 10)

    #creates bus
    bus_1 = model.create_element("PyPower.PQBus", QtCore.QPointF(275, 55))
    model.set_param_value(bus_1, 'base_kv', 20.00)

    #connect elements in the scenario
    model.set_pos(ElemPort(branch_1, '0'), QtCore.QPointF(220, 0))
    model.set_pos(ElemPort(branch_1, '1'), QtCore.QPointF(275, 55))
    #dock elements in the model
    model.dock(ElemPort(branch_1, '0'), ElemPort(refbus_1, '0'))
    model.dock(ElemPort(branch_1, '1'), ElemPort(bus_1, '0'))

    #creates PQBus
    bus_2 = model.create_element("PyPower.PQBus", QtCore.QPointF(275, 220))
    model.set_param_value(bus_2, 'base_kv', 0.23)

    #creates Transformer
    transformer_1 = model.create_element('PyPower.Transformer', QtCore.QPointF())
    model.set_param_value(transformer_1, 'ttype', 'TRAFO_250')

    #connect Transformer
    model.set_pos(ElemPort(transformer_1, '0'), QtCore.QPointF(275, 55))
    model.set_pos(ElemPort(transformer_1, '1'), QtCore.QPointF(275, 220))
    model.dock(ElemPort(transformer_1, '0'), ElemPort(bus_1, '0'))
    model.dock(ElemPort(transformer_1, '1'), ElemPort(bus_2, '0'))

    #creates PQBus
    bus_3 = model.create_element("PyPower.PQBus", QtCore.QPointF(165, 220))
    model.set_param_value(bus_3, 'base_kv', 0.23)

    #creates Branch
    branch_2 = model.create_element("PyPower.Branch", QtCore.QPointF())
    model.set_param_value(branch_2, 'btype', 'NAYY_120')
    model.set_param_value(branch_2, 'online', True)
    model.set_param_value(branch_2, 'l', 0.6)

    #connect elements in the scenario
    model.set_pos(ElemPort(branch_2, '0'), QtCore.QPointF(275, 220))
    model.set_pos(ElemPort(branch_2, '1'), QtCore.QPointF(165, 220))
    #dock elements in the model
    model.dock(ElemPort(branch_2, '0'), ElemPort(bus_2, '0'))
    model.dock(ElemPort(branch_2, '1'), ElemPort(bus_3, '0'))

    #creates PQBus
    bus_4 = model.create_element("PyPower.PQBus", QtCore.QPointF(440, 220))
    model.set_param_value(bus_4, 'base_kv', 0.23)

    #creates Branch
    branch_3 = model.create_element("PyPower.Branch", QtCore.QPointF())
    model.set_param_value(branch_3, 'btype', 'NAYY_120')
    model.set_param_value(branch_3, 'online', True)
    model.set_param_value(branch_3, 'l', 1.2)

    #connect elements in the scenario
    model.set_pos(ElemPort(branch_3, '0'), QtCore.QPointF(275, 220))
    model.set_pos(ElemPort(branch_3, '1'), QtCore.QPointF(440, 220))
    #dock elements in the model
    model.dock(ElemPort(branch_3, '0'), ElemPort(bus_2, '0'))
    model.dock(ElemPort(branch_3, '1'), ElemPort(bus_4, '0'))

    #creates PQBus
    bus_5 = model.create_element("PyPower.PQBus", QtCore.QPointF(110, 385))
    model.set_param_value(bus_5, 'base_kv', 0.23)

    #creates Branch
    branch_4 = model.create_element("PyPower.Branch", QtCore.QPointF())
    model.set_param_value(branch_4, 'btype', 'NAYY_120')
    model.set_param_value(branch_4, 'online', True)
    model.set_param_value(branch_4, 'l', 0.1)

    #connect elements in the scenario
    model.set_pos(ElemPort(branch_4, '0'), QtCore.QPointF(165, 220))
    model.set_pos(ElemPort(branch_4, '1'), QtCore.QPointF(110, 385))
    #dock elements in the model
    model.dock(ElemPort(branch_4, '0'), ElemPort(bus_3, '0'))
    model.dock(ElemPort(branch_4, '1'), ElemPort(bus_5, '0'))

    #creates PQBus
    bus_6 = model.create_element("PyPower.PQBus", QtCore.QPointF(495, 385))
    model.set_param_value(bus_6, 'base_kv', 0.23)

    #creates Branch
    branch_5 = model.create_element("PyPower.Branch", QtCore.QPointF())
    model.set_param_value(branch_5, 'btype', 'NAYY_120')
    model.set_param_value(branch_5, 'online', True)
    model.set_param_value(branch_5, 'l', 0.4)

    #connect elements in the scenario
    model.set_pos(ElemPort(branch_5, '0'), QtCore.QPointF(440, 220))
    model.set_pos(ElemPort(branch_5, '1'), QtCore.QPointF(495, 385))
    #dock elements in the model
    model.dock(ElemPort(branch_5, '0'), ElemPort(bus_4, '0'))
    model.dock(ElemPort(branch_5, '1'), ElemPort(bus_6, '0'))

    #                                                                       #
    #------------------------------- PVs------------------------------------#
    #                                                                       #

    pv_1 = model.create_element("CSV.PV", QtCore.QPointF(385, 55))
    model.set_pos(ElemPort(pv_1, '1'), QtCore.QPointF(275, 55))
    model.set_param_value(pv_1, 'datafile', 'maverig/tests/data/pv_30kw.small.csv')
    model.dock(ElemPort(pv_1, '1'), ElemPort(bus_1, '0'))

    pv_2 = model.create_element("CSV.PV", QtCore.QPointF(0, 385))
    model.set_pos(ElemPort(pv_2, '1'), QtCore.QPointF(110, 385))
    model.set_param_value(pv_2, 'datafile', 'maverig/tests/data/pv_10kw.small.csv')
    model.dock(ElemPort(pv_2, '1'), ElemPort(bus_5, '0'))

    pv_3 = model.create_element("CSV.PV", QtCore.QPointF(550, 385))
    model.set_pos(ElemPort(pv_3, '1'), QtCore.QPointF(495, 385))
    model.set_param_value(pv_3, 'datafile', 'maverig/tests/data/pv_10kw.small.csv')
    model.dock(ElemPort(pv_3, '1'), ElemPort(bus_6, '0'))

    #                                                                        #
    #-------------------- Wind Energy Conversion Systems --------------------#
    #                                                                        #

    wecs_1 = model.create_element("CSV.WECS", QtCore.QPointF(330, 0))
    model.set_pos(ElemPort(wecs_1, '1'), QtCore.QPointF(275, 55))
    model.set_param_value(wecs_1, 'datafile', 'maverig/tests/data/wecs_2000kw.small.csv')
    model.dock(ElemPort(wecs_1, '1'), ElemPort(bus_1, '0'))

    wecs_2 = model.create_element("CSV.WECS", QtCore.QPointF(275, 275))
    model.set_pos(ElemPort(wecs_2, '1'), QtCore.QPointF(275, 220))
    model.set_param_value(wecs_2, 'datafile', 'maverig/tests/data/wecs_10kw.small.csv')
    model.dock(ElemPort(wecs_2, '1'), ElemPort(bus_2, '0'))

    #                                                                        #
    #--------------------------- Electric Vehicles --------------------------#
    #                                                                        #

    ev_1 = model.create_element('CSV.EV', QtCore.QPointF(165, 385))
    model.set_pos(ElemPort(ev_1, '1'), QtCore.QPointF(110, 385))
    model.set_param_value(ev_1, 'datafile', 'maverig/tests/data/ev.small.csv')
    model.dock(ElemPort(ev_1, '1'), ElemPort(bus_5, '0'))

    #                                                                        #
    #------------------------ Combined Heat and Power -----------------------#
    #                                                                        #

    chp_1 = model.create_element('CSV.CHP', QtCore.QPointF(440, 385))
    model.set_pos(ElemPort(chp_1, '1'), QtCore.QPointF(495, 385))
    model.set_param_value(chp_1, 'datafile', 'maverig/tests/data/chp.small.csv')
    model.dock(ElemPort(chp_1, '1'), ElemPort(bus_6, '0'))

    #                                                                        #
    #------------------------------- Households -----------------------------#
    #                                                                        #

    house_1 = model.create_element('CSV.House', QtCore.QPointF(110, 110))
    model.set_pos(ElemPort(house_1, '1'), QtCore.QPointF(165, 220))
    model.set_param_value(house_1, 'datafile', 'maverig/tests/data/household_1_2.small.csv')
    model.dock(ElemPort(house_1, '1'), ElemPort(bus_3, '0'))

    house_2 = model.create_element('CSV.House', QtCore.QPointF(55, 220))
    model.set_pos(ElemPort(house_2, '1'), QtCore.QPointF(165, 220))
    model.set_param_value(house_2, 'datafile', 'maverig/tests/data/household_1_4.small.csv')
    model.dock(ElemPort(house_2, '1'), ElemPort(bus_3, '0'))

    house_3 = model.create_element('CSV.House', QtCore.QPointF(55, 440))
    model.set_pos(ElemPort(house_3, '1'), QtCore.QPointF(110, 385))
    model.set_param_value(house_3, 'datafile', 'maverig/tests/data/household_3_4.small.csv')
    model.dock(ElemPort(house_3, '1'), ElemPort(bus_5, '0'))

    house_4 = model.create_element('CSV.House', QtCore.QPointF(495, 165))
    model.set_pos(ElemPort(house_4, '1'), QtCore.QPointF(440, 220))
    model.set_param_value(house_4, 'datafile', 'maverig/tests/data/household_1_4.small.csv')
    model.dock(ElemPort(house_4, '1'), ElemPort(bus_4, '0'))

    house_5 = model.create_element('CSV.House', QtCore.QPointF(550, 440))
    model.set_pos(ElemPort(house_5, '1'), QtCore.QPointF(495, 385))
    model.set_param_value(house_5, 'datafile', 'maverig/tests/data/household_3_4.small.csv')
    model.dock(ElemPort(house_5, '1'), ElemPort(bus_6, '0'))

    model.init_history()
    model.update_all()
    entry_point.main_window.show()
    try:
        sys.exit(app.exec_())
    except (KeyboardInterrupt, SystemExit):
        model.simulation.stop()
        raise


if __name__ == '__main__':
    main()