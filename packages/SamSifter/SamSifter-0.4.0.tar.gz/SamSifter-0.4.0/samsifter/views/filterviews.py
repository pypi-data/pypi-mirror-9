# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 09:38:31 2014

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" Qt4 """
from PyQt4.QtGui import (QAbstractItemView, QListView, QTreeWidget)


class FilterTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(FilterTreeWidget, self).__init__(parent)
#        self.setHeaderHidden(True)


class FilterListView(QListView):
    def __init__(self, parent=None):
        super(FilterListView, self).__init__(parent)
        self.viewport().setAutoFillBackground(True)
#        self.setAcceptDrops(True)
#        self.setDragEnabled(True)
#        self.setDropIndicatorShown(True)
#        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
