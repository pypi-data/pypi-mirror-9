from PySide import QtGui, QtCore


class CellLineEdit(QtGui.QLineEdit):

    def __init__(self, table, cell_item):
        """ :type table: AutoRowTableWidget """
        super().__init__()
        self.setFrame(False)
        self.table = table
        self.cell_item = cell_item
        self.textChanged.connect(self.text_changed)

    def keyPressEvent(self, event):
        current_row = self.cell_item.row()
        current_col = self.cell_item.column()

        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            return self.table.setCurrentCell(current_row+1, max(current_col, 0))

        # remove empty row on backspace or delete key
        if event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete] \
                and self.table.rowCount() > 1 \
                and not self.table.row_has_text(current_row):
            return self.table.removeRow(current_row)
        super().keyPressEvent(event)

    def text_changed(self, text):
        """ add or remove rows according to last element content """
        last_row = self.table.rowCount() - 1

        if self.table.row_has_text(last_row):
            self.table.append_row()
        elif last_row > 0 and not self.table.row_has_text(last_row-1):
            self.table.removeRow(last_row)


class AutoRowTableWidget(QtGui.QTableWidget):
    """ Table Widget which always leaves one empty row as last row.
    RowCount is automatically adapted to cell contents."""

    def text(self, row, col):
        if not self.cellWidget(row, col):
            return None
        return self.cellWidget(row, col).text()

    def row_has_text(self, row):
        return any([self.text(row, col) for col in range(self.columnCount())])

    def append_row(self):
        new_row = self.rowCount()
        self.insertRow(new_row)
        for col in range(self.columnCount()):

            item = QtGui.QTableWidgetItem()
            self.setCellWidget(new_row, col, CellLineEdit(self, item))
            self.setItem(new_row, col, item)