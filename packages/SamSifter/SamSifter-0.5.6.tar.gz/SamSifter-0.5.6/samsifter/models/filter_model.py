#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filter models for trees and lists.

Implementations of the standard Qt4 item-based models for trees (2 dimensions)
and lists (1 dimension).

Warning
-------
Drag&Drop is *not* fully implemented due to restrictions on the binary encoding
of C++ objects using Python's ``pickle``. Pickling support is required to
encode filter items to MIME on initiation of a drag event as well as to decode
an item from MIME at the end of a drop event. However this would require the
implementation of (de)serialization methods for the entire hierarchy of
PyQt-wrapped C++ classes that are used in this project and currently don't
support ``pickle``.


Thus, I have decided to simply override the double-click behaviour on filter
items to emulate the *drag&drop* action with a similarly intuitive
*click&clone* action. See :py:meth:`samsifter.models.filter.FilterItem.clone`
and :py:meth:`samsifter.samsifter.MainWindow.init_ui` for details.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" Qt4 """
from PyQt4.QtGui import QStandardItemModel, QBrush, QColor
from PyQt4.QtCore import (Qt, QAbstractListModel, QModelIndex, pyqtSignal)


class FilterTreeModel(QStandardItemModel):
    """Item-based two-dimensional model for filter items.

    Can represent hierarchical and sequential data by implementing the
    QAbstractItemModel.
    """

    def __init__(self, parent=None):
        """Initialize new instance of filter list model.

        Parameters
        ----------
        parent : QObject, optional
            Parent Qt4 object this model belongs to, defaults to None.
        """
        super(FilterTreeModel, self).__init__(parent)
        self.setHorizontalHeaderLabels(["available filters"])

    def supportedDragActions(self):
        """Drag actions supported by the model.

        Used to return a combination of drop actions, indicating the types of
        drag and drop operations that the model accepts.

        Overrides Qt4 base method.

        Returns
        -------
        int
            Qt drag action.
        """
        return Qt.CopyAction

    def iterate_items(self):
        """Provides a lazy iterator over all filter items.

        Yields
        ------
        FilterItem
            Next filter item in model.
        """
        for i in range(self.rowCount()):
            yield self.item(i)


class FilterListModel(QAbstractListModel):
    """One-dimensional list model for filter items.

    Represents data as a simple non-hierarchical sequence of items.
    """

    item_changed = pyqtSignal('QStandardItem', name="itemChanged")

    def __init__(self, parent=None):
        """Initialize new instance of filter list model.

        Parameters
        ----------
        parent : QObject, optional
            Parent Qt4 object this model belongs to, defaults to None.
        """
        super(FilterListModel, self).__init__(parent)
        self.filters = []

    def __repr__(self):
        """String representation of model for debugging."""
        rep = "\nmodel contains %i filters:" % len(self.filters)
        for fltr in self.filters:
            rep += repr(fltr)
        return rep

    def flags(self, index):
        """Provides view with Qt flags for item at given index.

        Must return an appropriate combination of flags for each item. In
        particular, the value returned by this function must include
        Qt::ItemIsEditable in addition to the values applied to items in a
        read-only model.

        Used by other components to obtain information about each item provided
        by the model. In many models, the combination of flags should include
        Qt::ItemIsEnabled and Qt::ItemIsSelectable.

        Implements abstract Qt4 method.

        Parameters
        ----------
        index : QModelIndex
            Model index of requested item.

        Returns
        -------
        int
            Combination of bit flags for item properties.
        """
        if index.isValid():
            return(Qt.ItemIsEnabled | Qt.ItemIsSelectable
                   | Qt.ItemIsDropEnabled)
        return Qt.ItemIsDropEnabled

    """ data """

    def iterate_items(self):
        """Provides a lazy iterator over all filter items.

        Yields
        ------
        FilterItem
            The next filter item in the model.
        """
        for i in range(len(self.filters)):
            yield self.filters[i]

    def index(self, row, col=0, parent=QModelIndex()):
        """Returns the index of the specified model item.

        Implements abstract Qt4 base method.

        Parameters
        ----------
        row : int
            Model row.
        col : int, optional
            Model column, defaults to 0 (list only has one column).
        parent : QModelIndex, optional
            Model index of parent item, defaults to invalid QModelIndex.

        Returns
        -------
        QModelIndex
            Model index of specified item (invalid if non-existant).
        """
        return self.createIndex(row, col)

    def data(self, index, role=Qt.DisplayRole):
        """Supplies item data to views and delegates.

        Generally, models only need to supply data for Qt.DisplayRole and any
        application-specific Qt.AccessibleTextRole, and
        Qt.AccessibleDescriptionRole. See the Qt.ItemDataRole enum
        documentation for information about the types
        associated with each role.

        Implements abstract Qt4 base method.

        Parameters
        ----------
        index : QModelIndex
            Model index of requested content item.
        role : int
            Qt item data role, defaults to DisplayRole.

        Returns
        -------
        any
            Depending on model data and requested role.
        None
            If index is invalid.
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
            return item.get_description()
        return None

    def insertItem(self, item, row=None):
        """Insert filter item at specified position or append at end.

        Implements abstract Qt4 base method.

        Parameters
        ----------
        item : FilterItem
            Item to be inserted.
        row : int, optional
            Target row, defaults to None resulting in insertion at the end.

        Returns
        -------
        bool
            True on success.
        """
        if row is None:
            row = len(self.filters)
        self.beginInsertRows(QModelIndex(), row, row)
        self.filters.insert(row, item)
        self.endInsertRows()
        self.rowsInserted.emit(QModelIndex(), row, row)
        return True

    def takeItem(self, row=None):
        """Retrieves item and remove corresponding row.

        Implements abstract Qt4 base method.

        Parameters
        ----------
        row : int, optional
            Target row, defaults to None resulting in deletion from the end.

        Returns
        -------
        None
            If given row is smaller or larger than model.
        FilterItem
            Requested filter item.
        """
        if row is None:
            row = len(self.filters) - 1
        if row >= len(self.filters) or row < 0:
            return None

        item = self.filters[row]
        self.removeRow(row)
        return item

    def removeRows(self, row, count, parent=QModelIndex()):
        """Remove several rows at once.

        Used to remove rows and the items of data they contain from all types
        of model. Implementations must call beginRemoveRows() before inserting
        new columns into any underlying data structures, and call
        endRemoveRows() immediately afterwards.

        Implements abstract Qt4 base method.

        Parameters
        ----------
        row : int
            Start row of the range to be removed.
        count : int
            Number of rows to be removed including the start row.
        parent : QModelIndex, optional
            Parent of the item to be removed, defaults to invalid index.

        Returns
        -------
        bool
            True on success, False on valid index or invalid row number.
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
        """Remove a single row.

        Implements abstract Qt4 base method.

        Parameters
        ----------
        row : int
            Start row of the range to be removed.
        parent : QModelIndex, optional
            Parent of the item to be removed, defaults to invalid index.

        Returns
        -------
        bool
            True on success, False on valid index or invalid row number.
        """
        return self.removeRows(row, 1, parent)

    def removeAll(self, parent=QModelIndex()):
        """Remove all rows.

        Implements abstract Qt4 base method.

        Parameters
        ----------
        parent : QModelIndex, optional
            Parent of the item to be removed, defaults to invalid index.

        Returns
        -------
        bool
            True on success.
        """
        return self.removeRows(0, self.rowCount(), parent)

    def rowCount(self, parent=QModelIndex()):
        """Provides the number of rows of data exposed by the model.

        Implements abstract Qt4 base method.

        Returns
        -------
        int
            Number of items (= rows) in model.
        """
        if parent.isValid():
            return 0
        else:
            return len(self.filters)

    """ drag and drop """

    def supportedDropActions(self):
        """Drop actions supported by the model.

        Used to return a combination of drop actions, indicating the types of
        drop operations that the model accepts.

        Overrides Qt4 base method.

        Returns
        -------
        int
            Combination of Qt drop actions (bit flags).
        """
        return Qt.CopyAction | Qt.MoveAction

    def supportedDragActions(self):
        """Drag actions supported by the model.

        Used to return a combination of drop actions, indicating the types of
        drag and drop operations that the model accepts.

        Overrides Qt4 base method.

        Returns
        -------
        int
            Combination of Qt drag actions (bit flags).
        """
        return Qt.MoveAction
