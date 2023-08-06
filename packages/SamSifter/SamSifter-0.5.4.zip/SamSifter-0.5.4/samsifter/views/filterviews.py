# -*- coding: utf-8 -*-
"""
Extensions of standard Qt views for trees and lists.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" Qt4 """
from PyQt4.QtGui import (QAbstractItemView, QListView, QTreeWidget)


class FilterTreeWidget(QTreeWidget):
    """Tree widget for filter items.

    Used for hierarchical classification of tools and filters in the dock
    widget showing available workflow actions.

    Note
    ----
    See :py:class:`samsifter.models.filter_model.FilterTreeModel` for details
    on the current status of Drap&Drop implementation.
    """

    def __init__(self, parent=None):
        super(FilterTreeWidget, self).__init__(parent)
#        self.setAcceptDrops(True)
#        self.setDragEnabled(True)
#        self.setDropIndicatorShown(True)
#        self.setDefaultDropAction(Qt.MoveAction)
#        self.setHeaderHidden(True)


class FilterListView(QListView):
    """List view for filter items.

    Used for the listing of consecutive filter actions in the main window.

    Note
    ----
    See :py:class:`samsifter.models.filter_model.FilterListModel` for details
    on the current status of Drap&Drop implementation.
    """

    def __init__(self, parent=None):
        super(FilterListView, self).__init__(parent)
        self.viewport().setAutoFillBackground(True)
#        self.setAcceptDrops(True)
#        self.setDragEnabled(True)
#        self.setDropIndicatorShown(True)
#        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
