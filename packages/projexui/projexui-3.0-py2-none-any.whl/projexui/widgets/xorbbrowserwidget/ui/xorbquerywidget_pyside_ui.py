# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xorbbrowserwidget\ui\xorbquerywidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(425, 220)
        Form.setMinimumSize(QtCore.QSize(425, 220))
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.uiAddBTN = QtGui.QToolButton(Form)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/default/img/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiAddBTN.setIcon(icon)
        self.uiAddBTN.setAutoRaise(True)
        self.uiAddBTN.setObjectName("uiAddBTN")
        self.gridLayout.addWidget(self.uiAddBTN, 0, 1, 1, 1)
        self.uiRemoveBTN = QtGui.QToolButton(Form)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/default/img/remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiRemoveBTN.setIcon(icon1)
        self.uiRemoveBTN.setAutoRaise(True)
        self.uiRemoveBTN.setObjectName("uiRemoveBTN")
        self.gridLayout.addWidget(self.uiRemoveBTN, 0, 3, 1, 1)
        self.uiQueryTREE = XTreeWidget(Form)
        self.uiQueryTREE.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.uiQueryTREE.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.uiQueryTREE.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.uiQueryTREE.setIndentation(10)
        self.uiQueryTREE.setProperty("x_arrowStyle", True)
        self.uiQueryTREE.setProperty("x_showGridColumns", False)
        self.uiQueryTREE.setObjectName("uiQueryTREE")
        self.uiQueryTREE.header().setVisible(False)
        self.gridLayout.addWidget(self.uiQueryTREE, 1, 0, 1, 4)
        self.uiQueryTXT = XLineEdit(Form)
        self.uiQueryTXT.setObjectName("uiQueryTXT")
        self.gridLayout.addWidget(self.uiQueryTXT, 0, 0, 1, 1)
        self.uiGroupBTN = QtGui.QToolButton(Form)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/default/img/group.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiGroupBTN.setIcon(icon2)
        self.uiGroupBTN.setAutoRaise(True)
        self.uiGroupBTN.setObjectName("uiGroupBTN")
        self.gridLayout.addWidget(self.uiGroupBTN, 0, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.uiAddBTN.setToolTip(QtGui.QApplication.translate("Form", "Add Query", None, QtGui.QApplication.UnicodeUTF8))
        self.uiAddBTN.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRemoveBTN.setToolTip(QtGui.QApplication.translate("Form", "Remove Query", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRemoveBTN.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.uiQueryTREE.headerItem().setText(0, QtGui.QApplication.translate("Form", "Column", None, QtGui.QApplication.UnicodeUTF8))
        self.uiQueryTREE.headerItem().setText(1, QtGui.QApplication.translate("Form", "Operator", None, QtGui.QApplication.UnicodeUTF8))
        self.uiQueryTREE.headerItem().setText(2, QtGui.QApplication.translate("Form", "Data", None, QtGui.QApplication.UnicodeUTF8))
        self.uiQueryTXT.setProperty("x_hint", QtGui.QApplication.translate("Form", "type a query or leave blank and click the add button", None, QtGui.QApplication.UnicodeUTF8))
        self.uiGroupBTN.setToolTip(QtGui.QApplication.translate("Form", "Group Selection", None, QtGui.QApplication.UnicodeUTF8))
        self.uiGroupBTN.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xtreewidget import XTreeWidget
from projexui.widgets.xlineedit import XLineEdit

