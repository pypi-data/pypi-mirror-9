# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xlogrecordwidget\ui\xlogrecordcontrols.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_XLogRecordControls(object):
    def setupUi(self, XLogRecordControls):
        XLogRecordControls.setObjectName("XLogRecordControls")
        XLogRecordControls.resize(400, 275)
        XLogRecordControls.setMinimumSize(QtCore.QSize(400, 275))
        self.gridLayout_3 = QtGui.QGridLayout(XLogRecordControls)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.uiMainTAB = QtGui.QTabWidget(XLogRecordControls)
        self.uiMainTAB.setObjectName("uiMainTAB")
        self.uiLevelPAGE = QtGui.QWidget()
        self.uiLevelPAGE.setObjectName("uiLevelPAGE")
        self.gridLayout_2 = QtGui.QGridLayout(self.uiLevelPAGE)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.uiLevelTREE = XTreeWidget(self.uiLevelPAGE)
        self.uiLevelTREE.setMaximumSize(QtCore.QSize(16777215, 160))
        self.uiLevelTREE.setAlternatingRowColors(True)
        self.uiLevelTREE.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.uiLevelTREE.setRootIsDecorated(False)
        self.uiLevelTREE.setObjectName("uiLevelTREE")
        self.uiLevelTREE.header().setVisible(False)
        self.gridLayout_2.addWidget(self.uiLevelTREE, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.uiLevelPAGE)
        self.label.setEnabled(False)
        self.label.setWordWrap(True)
        self.label.setIndent(6)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.uiMainTAB.addTab(self.uiLevelPAGE, "")
        self.uiLoggerPAGE = QtGui.QWidget()
        self.uiLoggerPAGE.setObjectName("uiLoggerPAGE")
        self.gridLayout = QtGui.QGridLayout(self.uiLoggerPAGE)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.uiLoggerTREE = XLoggerTreeWidget(self.uiLoggerPAGE)
        self.uiLoggerTREE.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.SelectedClicked)
        self.uiLoggerTREE.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.uiLoggerTREE.setObjectName("uiLoggerTREE")
        self.uiLoggerTREE.header().setVisible(False)
        self.gridLayout.addWidget(self.uiLoggerTREE, 0, 0, 1, 1)
        self.uiInfoLBL = QtGui.QLabel(self.uiLoggerPAGE)
        self.uiInfoLBL.setEnabled(False)
        self.uiInfoLBL.setIndent(6)
        self.uiInfoLBL.setObjectName("uiInfoLBL")
        self.gridLayout.addWidget(self.uiInfoLBL, 1, 0, 1, 1)
        self.uiMainTAB.addTab(self.uiLoggerPAGE, "")
        self.gridLayout_3.addWidget(self.uiMainTAB, 0, 0, 1, 1)

        self.retranslateUi(XLogRecordControls)
        self.uiMainTAB.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(XLogRecordControls)

    def retranslateUi(self, XLogRecordControls):
        XLogRecordControls.setWindowTitle(QtGui.QApplication.translate("XLogRecordControls", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.uiLevelTREE.headerItem().setText(0, QtGui.QApplication.translate("XLogRecordControls", "Level", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("XLogRecordControls", "If no levels are selected, then no filter will be applied and all messages will be displayed.", None, QtGui.QApplication.UnicodeUTF8))
        self.uiMainTAB.setTabText(self.uiMainTAB.indexOf(self.uiLevelPAGE), QtGui.QApplication.translate("XLogRecordControls", "Levels", None, QtGui.QApplication.UnicodeUTF8))
        self.uiLoggerTREE.headerItem().setText(0, QtGui.QApplication.translate("XLogRecordControls", "Logger", None, QtGui.QApplication.UnicodeUTF8))
        self.uiLoggerTREE.headerItem().setText(1, QtGui.QApplication.translate("XLogRecordControls", "Level", None, QtGui.QApplication.UnicodeUTF8))
        self.uiInfoLBL.setText(QtGui.QApplication.translate("XLogRecordControls", "This will affect the global logger levels", None, QtGui.QApplication.UnicodeUTF8))
        self.uiMainTAB.setTabText(self.uiMainTAB.indexOf(self.uiLoggerPAGE), QtGui.QApplication.translate("XLogRecordControls", "Loggers", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xloggerwidget import XLoggerTreeWidget
from projexui.widgets.xtreewidget import XTreeWidget

