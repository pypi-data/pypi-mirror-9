#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 09:19:24 2014

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" Qt4 """
from PyQt4.QtGui import QStandardItemModel, QBrush, QColor
from PyQt4.QtCore import (Qt, QAbstractListModel, QModelIndex, pyqtSignal)


class FilterTreeModel(QStandardItemModel):
    """
    Item-based two-dimensional model for filter items.

    Can represent hierarchical and sequential data by implementing the
    QAbstractItemModel.

    TODO: allow external drag&drop of custom items, not only StandardItem
    """
    def __init__(self, parent=None):
        super(FilterTreeModel, self).__init__(parent)
        self.setHorizontalHeaderLabels(["available filters"])

    def supportedDragActions(self):
        """
        Used to return a combination of drop actions, indicating the types of
        drag and drop operations that the model accepts.

        NOTE: Subclassed method, hence the unpythonic name.
        """
        return Qt.CopyAction

    def iterate_items(self):
        """
        Provides a lazy iterator over all filter items.
        """
        for i in range(self.rowCount()):
            yield self.item(i)


class SimpleFilterListModel(QAbstractListModel):
    """
    One-dimensional list model for filter items.

    Represents data as a simple non-hierarchical sequence of items.
    """

    item_changed = pyqtSignal('QStandardItem', name="itemChanged")

    def __init__(self, parent=None):
        super(SimpleFilterListModel, self).__init__(parent)
        self.filters = []

    def __repr__(self):
        rep = "\nmodel contains %i filters:" % len(self.filters)
        for fltr in self.filters:
            rep += repr(fltr)
        return rep

    def flags(self, index):
        """
        Must return an appropriate combination of flags for each item. In
        particular, the value returned by this function must include
        Qt::ItemIsEditable in addition to the values applied to items in a
        read-only model.

        Used by other components to obtain information about each item provided
        by the model. In many models, the combination of flags should include
        Qt::ItemIsEnabled and Qt::ItemIsSelectable.
        """
        if index.isValid():
            return(Qt.ItemIsEnabled | Qt.ItemIsSelectable
                   | Qt.ItemIsDropEnabled)
        return Qt.ItemIsDropEnabled

    """ data """

    def iterate_items(self):
        """
        Provides a lazy iterator over all filter items.
        """
        for i in range(len(self.filters)):
            yield self.filters[i]

    def index(self, row, col=0, parent=QModelIndex()):
        """
        Returns the index of the item in the model specified by the given row,
        column and parent index.
        """
        return self.createIndex(row, col)

    def data(self, index, role=Qt.DisplayRole):
        """
        Used to supply item data to views and delegates. Generally, models only
        need to supply data for Qt::DisplayRole and any application-specific
        Qt::AccessibleTextRole, and Qt::AccessibleDescriptionRole. See the
        Qt::ItemDataRole enum documentation for information about the types
        associated with each role.
        """
        if not index.isValid():
            return None

        try:
            item = self.filters[index.row()]
        except IndexError:
            return None

        if role == Qt.DisplayRole:
            return item.text()
        elif role == Qt.DecorationRole:
            return item.icon()
        elif role == Qt.UserRole:
            return item
        elif role == Qt.ForegroundRole:
            if item.is_valid():
                return QBrush(Qt.black)
            else:
                return QBrush(Qt.red)
        elif role == Qt.BackgroundRole:
            if item.is_valid():
                return QBrush(Qt.white)
            else:
                return QBrush(QColor(255, 224, 140, 255))
        elif role == Qt.ToolTipRole:
            return item.getDesc()
        return None

    def insertItem(self, item, row=None):
        """
        Insert filter item at specified position or append at end.
        """
        if row is None:
            row = len(self.filters)
        self.beginInsertRows(QModelIndex(), row, row)
        self.filters.insert(row, item)
        self.endInsertRows()
        self.rowsInserted.emit(QModelIndex(), row, row)
        return True

    def takeItem(self, row=None):
        """
        Retrieve item and remove corresponding row.
        """
        if row is None:
            row = len(self.filters) - 1
        if row >= len(self.filters) or row < 0:
            return None

        item = self.filters[row]
        self.removeRow(row)
        return item

    def removeRows(self, row, count, parent=QModelIndex()):
        """
        Used to remove rows and the items of data they contain from all types
        of model. Implementations must call beginRemoveRows() before inserting
        new columns into any underlying data structures, and call
        endRemoveRows() immediately afterwards.
        """
        if parent.isValid():
            return False

        if row >= len(self.filters) or row + count <= 0:
            return False

        begin_row = max(0, row)
        end_row = min(row + count - 1, len(self.filters) - 1)
        self.beginRemoveRows(parent, begin_row, end_row)
        self.filters = self.filters[:begin_row] + self.filters[end_row + 1:]
        self.endRemoveRows()
        self.rowsRemoved.emit(parent, begin_row, end_row)
        return True

    def removeRow(self, row, parent=QModelIndex()):
        return self.removeRows(row, 1, parent)

    def removeAll(self, parent=QModelIndex()):
        return self.removeRows(0, self.rowCount(), parent)

    def rowCount(self, parent=QModelIndex()):
        """
        Provides the number of rows of data exposed by the model.
        """
        if parent.isValid():
            return 0
        else:
            return len(self.filters)

    """ drag and drop """

    def supportedDropActions(self):
        """
        Used to return a combination of drop actions, indicating the types of
        drop operations that the model accepts.
        """
        return Qt.CopyAction | Qt.MoveAction

    def supportedDragActions(self):
        """
        Used to return a combination of drag actions, indicating the types of
        drag operations that the model accepts.
        """
        return Qt.MoveAction

    """ handlers """

#    def on_validity_change(self, item):
#        print("I am detecting a disturbance in the force.")
#        self.item_changed.emit()
