# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xlogrecordwidget\ui\xlogrecordwidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_XLogRecordWidget(object):
    def setupUi(self, XLogRecordWidget):
        XLogRecordWidget.setObjectName("XLogRecordWidget")
        XLogRecordWidget.resize(546, 386)
        self.gridLayout = QtGui.QGridLayout(XLogRecordWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.uiRecordBTN = XToolButton(XLogRecordWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/default/img/debug/break.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiRecordBTN.setIcon(icon)
        self.uiRecordBTN.setCheckable(True)
        self.uiRecordBTN.setChecked(True)
        self.uiRecordBTN.setProperty("x_shadowed", True)
        self.uiRecordBTN.setObjectName("uiRecordBTN")
        self.gridLayout.addWidget(self.uiRecordBTN, 0, 0, 1, 1)
        self.uiFilterTXT = XSearchEdit(XLogRecordWidget)
        self.uiFilterTXT.setObjectName("uiFilterTXT")
        self.gridLayout.addWidget(self.uiFilterTXT, 0, 1, 1, 1)
        self.uiSettingsBTN = XPopupButton(XLogRecordWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/default/img/config.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiSettingsBTN.setIcon(icon1)
        self.uiSettingsBTN.setProperty("x_shadowed", True)
        self.uiSettingsBTN.setObjectName("uiSettingsBTN")
        self.gridLayout.addWidget(self.uiSettingsBTN, 0, 2, 1, 1)
        self.uiRecordTREE = XTreeWidget(XLogRecordWidget)
        self.uiRecordTREE.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiRecordTREE.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.uiRecordTREE.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.uiRecordTREE.setRootIsDecorated(False)
        self.uiRecordTREE.setProperty("x_showGrid", False)
        self.uiRecordTREE.setProperty("x_showGridColumns", False)
        self.uiRecordTREE.setObjectName("uiRecordTREE")
        self.gridLayout.addWidget(self.uiRecordTREE, 1, 0, 1, 3)
        self.uiFeedbackLBL = QtGui.QLabel(XLogRecordWidget)
        self.uiFeedbackLBL.setObjectName("uiFeedbackLBL")
        self.gridLayout.addWidget(self.uiFeedbackLBL, 2, 0, 1, 3)

        self.retranslateUi(XLogRecordWidget)
        QtCore.QObject.connect(self.uiFilterTXT, QtCore.SIGNAL("textChanged(QString)"), self.uiRecordTREE.filterItems)
        QtCore.QMetaObject.connectSlotsByName(XLogRecordWidget)

    def retranslateUi(self, XLogRecordWidget):
        XLogRecordWidget.setWindowTitle(QtGui.QApplication.translate("XLogRecordWidget", "Log Record Widget", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordBTN.setToolTip(QtGui.QApplication.translate("XLogRecordWidget", "<html><head/><body><p>Toggle Active Listening</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.uiFilterTXT.setProperty("x_hint", QtGui.QApplication.translate("XLogRecordWidget", "filter records", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.setProperty("x_hint", QtGui.QApplication.translate("XLogRecordWidget", "No logging records have been found.  To setup logging, you can use the config panel on the top right button.", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(0, QtGui.QApplication.translate("XLogRecordWidget", "Level", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(1, QtGui.QApplication.translate("XLogRecordWidget", "Level #", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(2, QtGui.QApplication.translate("XLogRecordWidget", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(3, QtGui.QApplication.translate("XLogRecordWidget", "Created at", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(4, QtGui.QApplication.translate("XLogRecordWidget", "Message", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(5, QtGui.QApplication.translate("XLogRecordWidget", "Relative time (secs)", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(6, QtGui.QApplication.translate("XLogRecordWidget", "Filename", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(7, QtGui.QApplication.translate("XLogRecordWidget", "Module", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(8, QtGui.QApplication.translate("XLogRecordWidget", "Function", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(9, QtGui.QApplication.translate("XLogRecordWidget", "Line #", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(10, QtGui.QApplication.translate("XLogRecordWidget", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(11, QtGui.QApplication.translate("XLogRecordWidget", "Process ID", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(12, QtGui.QApplication.translate("XLogRecordWidget", "Process Name", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(13, QtGui.QApplication.translate("XLogRecordWidget", "Thread", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.headerItem().setText(14, QtGui.QApplication.translate("XLogRecordWidget", "Thread Name", None, QtGui.QApplication.UnicodeUTF8))
        self.uiFeedbackLBL.setText(QtGui.QApplication.translate("XLogRecordWidget", "Main thread: <none>", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xpopupbutton import XPopupButton
from projexui.widgets.xtreewidget import XTreeWidget
from projexui.widgets.xtoolbutton import XToolButton
from projexui.widgets.xsearchedit import XSearchEdit

