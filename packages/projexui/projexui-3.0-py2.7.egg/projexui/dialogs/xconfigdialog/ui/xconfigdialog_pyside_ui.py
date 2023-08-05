# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\dialogs\xconfigdialog\ui\xconfigdialog.ui'
#
# Created: Wed Dec 31 14:09:28 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_XConfigDialog(object):
    def setupUi(self, XConfigDialog):
        XConfigDialog.setObjectName("XConfigDialog")
        XConfigDialog.resize(666, 401)
        self.gridLayout = QtGui.QGridLayout(XConfigDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiMainSPLT = QtGui.QSplitter(XConfigDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiMainSPLT.sizePolicy().hasHeightForWidth())
        self.uiMainSPLT.setSizePolicy(sizePolicy)
        self.uiMainSPLT.setOrientation(QtCore.Qt.Horizontal)
        self.uiMainSPLT.setObjectName("uiMainSPLT")
        self.uiPluginTREE = XTreeWidget(self.uiMainSPLT)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPluginTREE.sizePolicy().hasHeightForWidth())
        self.uiPluginTREE.setSizePolicy(sizePolicy)
        self.uiPluginTREE.setMinimumSize(QtCore.QSize(150, 0))
        self.uiPluginTREE.setRootIsDecorated(False)
        self.uiPluginTREE.setProperty("x_arrowStyle", True)
        self.uiPluginTREE.setProperty("x_showGrid", False)
        self.uiPluginTREE.setObjectName("uiPluginTREE")
        self.uiPluginTREE.headerItem().setText(0, "1")
        self.uiPluginTREE.header().setVisible(False)
        self.uiConfigSTACK = QtGui.QStackedWidget(self.uiMainSPLT)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.uiConfigSTACK.sizePolicy().hasHeightForWidth())
        self.uiConfigSTACK.setSizePolicy(sizePolicy)
        self.uiConfigSTACK.setFrameShape(QtGui.QFrame.Box)
        self.uiConfigSTACK.setFrameShadow(QtGui.QFrame.Sunken)
        self.uiConfigSTACK.setObjectName("uiConfigSTACK")
        self.gridLayout.addWidget(self.uiMainSPLT, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiResetBTN = QtGui.QPushButton(XConfigDialog)
        self.uiResetBTN.setObjectName("uiResetBTN")
        self.horizontalLayout.addWidget(self.uiResetBTN)
        self.uiSaveBTN = QtGui.QPushButton(XConfigDialog)
        self.uiSaveBTN.setObjectName("uiSaveBTN")
        self.horizontalLayout.addWidget(self.uiSaveBTN)
        self.uiSaveExitBTN = QtGui.QPushButton(XConfigDialog)
        self.uiSaveExitBTN.setObjectName("uiSaveExitBTN")
        self.horizontalLayout.addWidget(self.uiSaveExitBTN)
        self.uiCancelBTN = QtGui.QPushButton(XConfigDialog)
        self.uiCancelBTN.setObjectName("uiCancelBTN")
        self.horizontalLayout.addWidget(self.uiCancelBTN)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(XConfigDialog)
        self.uiConfigSTACK.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(XConfigDialog)

    def retranslateUi(self, XConfigDialog):
        XConfigDialog.setWindowTitle(QtGui.QApplication.translate("XConfigDialog", "Configure", None, QtGui.QApplication.UnicodeUTF8))
        self.uiResetBTN.setText(QtGui.QApplication.translate("XConfigDialog", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.uiSaveBTN.setText(QtGui.QApplication.translate("XConfigDialog", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.uiSaveExitBTN.setText(QtGui.QApplication.translate("XConfigDialog", "Save && Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.uiCancelBTN.setText(QtGui.QApplication.translate("XConfigDialog", "Exit", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xtreewidget import XTreeWidget
