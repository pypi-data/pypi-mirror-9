# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\configs\xshortcutconfig\ui\xshortcutwidget.ui'
#
# Created: Wed Dec 31 14:09:28 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(615, 325)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.uiActionTREE = QtGui.QTreeWidget(Form)
        self.uiActionTREE.setAlternatingRowColors(True)
        self.uiActionTREE.setRootIsDecorated(False)
        self.uiActionTREE.setObjectName("uiActionTREE")
        self.uiActionTREE.header().setStretchLastSection(False)
        self.gridLayout.addWidget(self.uiActionTREE, 0, 0, 2, 1)
        self.uiEditGRP = QtGui.QGroupBox(Form)
        self.uiEditGRP.setMaximumSize(QtCore.QSize(250, 16777215))
        self.uiEditGRP.setObjectName("uiEditGRP")
        self.verticalLayout = QtGui.QVBoxLayout(self.uiEditGRP)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.uiShortcutLBL = QtGui.QLabel(self.uiEditGRP)
        self.uiShortcutLBL.setObjectName("uiShortcutLBL")
        self.horizontalLayout_2.addWidget(self.uiShortcutLBL)
        self.uiShortcutTXT = QtGui.QLineEdit(self.uiEditGRP)
        self.uiShortcutTXT.setObjectName("uiShortcutTXT")
        self.horizontalLayout_2.addWidget(self.uiShortcutTXT)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiClearBTN = QtGui.QPushButton(self.uiEditGRP)
        self.uiClearBTN.setObjectName("uiClearBTN")
        self.horizontalLayout.addWidget(self.uiClearBTN)
        self.uiSaveBTN = QtGui.QPushButton(self.uiEditGRP)
        self.uiSaveBTN.setObjectName("uiSaveBTN")
        self.horizontalLayout.addWidget(self.uiSaveBTN)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addWidget(self.uiEditGRP, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 197, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Shortcuts", None, QtGui.QApplication.UnicodeUTF8))
        self.uiActionTREE.setSortingEnabled(True)
        self.uiActionTREE.headerItem().setText(0, QtGui.QApplication.translate("Form", "Action", None, QtGui.QApplication.UnicodeUTF8))
        self.uiActionTREE.headerItem().setText(1, QtGui.QApplication.translate("Form", "Shortcut", None, QtGui.QApplication.UnicodeUTF8))
        self.uiEditGRP.setTitle(QtGui.QApplication.translate("Form", "Edit Action", None, QtGui.QApplication.UnicodeUTF8))
        self.uiShortcutLBL.setText(QtGui.QApplication.translate("Form", "Shortcut:", None, QtGui.QApplication.UnicodeUTF8))
        self.uiClearBTN.setText(QtGui.QApplication.translate("Form", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.uiSaveBTN.setText(QtGui.QApplication.translate("Form", "Save", None, QtGui.QApplication.UnicodeUTF8))

