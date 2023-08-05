# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xganttwidget\ui\xganttwidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_XGanttWidget(object):
    def setupUi(self, XGanttWidget):
        XGanttWidget.setObjectName("XGanttWidget")
        XGanttWidget.resize(733, 462)
        self.gridLayout = QtGui.QGridLayout(XGanttWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.uiGanttSPLT = XSplitter(XGanttWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiGanttSPLT.sizePolicy().hasHeightForWidth())
        self.uiGanttSPLT.setSizePolicy(sizePolicy)
        self.uiGanttSPLT.setOrientation(QtCore.Qt.Horizontal)
        self.uiGanttSPLT.setObjectName("uiGanttSPLT")
        self.uiGanttTREE = XTreeWidget(self.uiGanttSPLT)
        self.uiGanttTREE.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.uiGanttTREE.setProperty("x_arrowStyle", True)
        self.uiGanttTREE.setObjectName("uiGanttTREE")
        self.uiGanttTREE.headerItem().setText(0, "Name")
        self.uiGanttVIEW = QtGui.QGraphicsView(self.uiGanttSPLT)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.uiGanttVIEW.sizePolicy().hasHeightForWidth())
        self.uiGanttVIEW.setSizePolicy(sizePolicy)
        self.uiGanttVIEW.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.uiGanttVIEW.setObjectName("uiGanttVIEW")
        self.gridLayout.addWidget(self.uiGanttSPLT, 0, 0, 1, 1)

        self.retranslateUi(XGanttWidget)
        QtCore.QMetaObject.connectSlotsByName(XGanttWidget)

    def retranslateUi(self, XGanttWidget):
        XGanttWidget.setWindowTitle(QtGui.QApplication.translate("XGanttWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.uiGanttTREE.headerItem().setText(1, QtGui.QApplication.translate("XGanttWidget", "Date Start", None, QtGui.QApplication.UnicodeUTF8))
        self.uiGanttTREE.headerItem().setText(2, QtGui.QApplication.translate("XGanttWidget", "Date End", None, QtGui.QApplication.UnicodeUTF8))
        self.uiGanttTREE.headerItem().setText(3, QtGui.QApplication.translate("XGanttWidget", "Days", None, QtGui.QApplication.UnicodeUTF8))
        self.uiGanttTREE.headerItem().setText(4, QtGui.QApplication.translate("XGanttWidget", "Weekdays", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xsplitter import XSplitter
from projexui.widgets.xtreewidget import XTreeWidget
