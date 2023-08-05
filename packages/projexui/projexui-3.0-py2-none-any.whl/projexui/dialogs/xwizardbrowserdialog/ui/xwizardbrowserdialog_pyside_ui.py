# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\dialogs\xwizardbrowserdialog\ui\xwizardbrowserdialog.ui'
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
        self.uiMainSPLT.setOrientation(QtCore.Qt.Horizontal)
        self.uiMainSPLT.setObjectName("uiMainSPLT")
        self.layoutWidget = QtGui.QWidget(self.uiMainSPLT)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiWizardTABLE = QtGui.QTableWidget(self.layoutWidget)
        self.uiWizardTABLE.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.uiWizardTABLE.setGridStyle(QtCore.Qt.NoPen)
        self.uiWizardTABLE.setObjectName("uiWizardTABLE")
        self.uiWizardTABLE.setColumnCount(0)
        self.uiWizardTABLE.setRowCount(0)
        self.verticalLayout.addWidget(self.uiWizardTABLE)
        self.uiDescriptionTXT = QtGui.QTextEdit(self.layoutWidget)
        self.uiDescriptionTXT.setReadOnly(True)
        self.uiDescriptionTXT.setObjectName("uiDescriptionTXT")
        self.verticalLayout.addWidget(self.uiDescriptionTXT)
        self.gridLayout.addWidget(self.uiMainSPLT, 0, 1, 1, 1)
        self.uiPluginTREE = XTreeWidget(XConfigDialog)
        self.uiPluginTREE.setMinimumSize(QtCore.QSize(200, 0))
        self.uiPluginTREE.setMaximumSize(QtCore.QSize(200, 16777215))
        self.uiPluginTREE.setRootIsDecorated(False)
        self.uiPluginTREE.setProperty("x_arrowStyle", True)
        self.uiPluginTREE.setProperty("x_showGrid", False)
        self.uiPluginTREE.setObjectName("uiPluginTREE")
        self.uiPluginTREE.headerItem().setText(0, "1")
        self.uiPluginTREE.header().setVisible(False)
        self.gridLayout.addWidget(self.uiPluginTREE, 0, 0, 1, 1)

        self.retranslateUi(XConfigDialog)
        QtCore.QMetaObject.connectSlotsByName(XConfigDialog)

    def retranslateUi(self, XConfigDialog):
        XConfigDialog.setWindowTitle(QtGui.QApplication.translate("XConfigDialog", "Wizard Browser", None, QtGui.QApplication.UnicodeUTF8))
        self.uiPluginTREE.setProperty("x_hint", QtGui.QApplication.translate("XConfigDialog", "No wizards were found.", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xtreewidget import XTreeWidget
