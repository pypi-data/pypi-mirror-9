#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 09:38:31 2014

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" Qt4 """
from PyQt4.QtGui import (QAbstractItemView, QListView, QPixmap, QDrag,
                         QListWidget, QTreeWidget)
from PyQt4.QtCore import (Qt, QDataStream, QIODevice, QByteArray, QMimeData,
                          QPoint)
""" custom libraries """
from samsifter.views.delegates import FilterItemDelegate
from samsifter.models.filter import FilterItem


class FilterTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(FilterTreeWidget, self).__init__(parent)
#        self.setHeaderHidden(True)


class FilterListWidget(QListWidget):
    def __init__(self, parent=None):
        super(FilterListWidget, self).__init__(parent)
#        self.insertItem(0, test_entry())
#        self.insertItem(0, test_entry2())

    def iterate_items(self):
        for i in range(self.count()):
            yield self.item(i)


class SimpleFilterListView(QListView):
    def __init__(self, parent=None):
        super(SimpleFilterListView, self).__init__(parent)
        # set transparent instead of white background
#        self.viewport().setAutoFillBackground(False)
        self.viewport().setAutoFillBackground(True)

#        self.setAcceptDrops(True)
#        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)


class FilterListView(QListView):
    """
    View of filter list according to MV pattern.

    Advantage over QListWidget is access to underlying item model, disadvantage
    is lack of setItemWidget() method; circumventing this by setIndexWidget()
    and some anti-pattern use of a parameter model within the FilterWidget.

    Some good advice taken from
    http://stackoverflow.com/questions/6452838/render-qwidget-in-paint-method-of-qwidgetdelegate-for-a-qlistview

    TODO: Drop the delegate class
    TODO: Call QListView.setIndexWidget() in the data() method of my model to
          set the widget
    TODO: Ensure no widget is already present when setting by checking
          QListView.indexWidget()
    TODO: Handle the Qt.SizeHintRole role to return the widget's size hint
    TODO: Return a blank QVariant for the Qt.DisplayRole role
    """
    def __init__(self, parent=None):
        super(FilterListView, self).__init__(parent)

        # set transparent instead of white background
#        self.viewport().setAutoFillBackground(False)
        self.viewport().setAutoFillBackground(True)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.CopyAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setItemDelegate(FilterItemDelegate(self))

    def setModel(self, model):
        QListView.setModel(self, model)
        self.refreshWidgets()

    def refreshWidgets(self):
        m = self.model()
        for idx in range(m.rowCount()):
            mdlidx = m.index(idx, 0)
            if self.indexWidget(mdlidx) is None:
                itm = m.getItem(idx)
                widget = itm.makeWidget()
                self.setIndexWidget(mdlidx, widget)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-filter"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-filter"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-filter"):

            # unpack the filter item
            data = event.mimeData().data("application/x-filter")
            stream = QDataStream(data, QIODevice.ReadOnly)
            item = FilterItem()
            stream >> item
#            item = pickle.loads(bstream)
#            self.model().appendRow(event.pos(), item)
            print("accepted %s of type %s" % (item, type(item)))

            idx = self.indexAt(event.pos())
            self.model().insertRow(item, idx.row())
            self.refreshWidgets()

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        # selected is the relevant filter object
        selected = self.model().data(index, Qt.UserRole)
#        selected = self.model().data(index, Qt.DisplayRole)
#        print("selected %s of type %s" % (selected, type(selected)))

        # pack the filter item
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        stream << selected
        mimeData = QMimeData()
        mimeData.setData("application/x-filter", data)

        drag = QDrag(self)
        drag.setMimeData(mimeData)

        # example 1 - the object itself
        pixmap = QPixmap()
        pixmap = pixmap.grabWidget(self, self.rectForIndex(index))

#        # example 2 -  a plain pixmap
#        pixmap = QPixmap(100, self.height()/2)
#        pixmap.fill(QColor("orange"))

        drag.setPixmap(pixmap)

        drag.setHotSpot(QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)
        if drag.start(Qt.MoveAction) == Qt.MoveAction:
            self.model().removeRow(index.row())

    def mouseMoveEvent(self, event):
        self.startDrag(event)
