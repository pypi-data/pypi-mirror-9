# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xorbquerywidget\ui\xorbquerycontainer.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(570, 140)
        Form.setMinimumSize(QtCore.QSize(570, 140))
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.uiNameTXT = XLineEdit(Form)
        self.uiNameTXT.setMinimumSize(QtCore.QSize(0, 32))
        self.uiNameTXT.setObjectName("uiNameTXT")
        self.gridLayout.addWidget(self.uiNameTXT, 0, 2, 1, 1)
        self.uiQueryAREA = QtGui.QScrollArea(Form)
        self.uiQueryAREA.setWidgetResizable(True)
        self.uiQueryAREA.setObjectName("uiQueryAREA")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 568, 106))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.uiQueryAREA.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.uiQueryAREA, 1, 0, 1, 4)
        self.uiBackBTN = QtGui.QToolButton(Form)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/default/img/query/back.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiBackBTN.setIcon(icon)
        self.uiBackBTN.setIconSize(QtCore.QSize(24, 24))
        self.uiBackBTN.setAutoRaise(True)
        self.uiBackBTN.setObjectName("uiBackBTN")
        self.gridLayout.addWidget(self.uiBackBTN, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.uiNameTXT.setProperty("x_hint", QtGui.QApplication.translate("Form", "custom compound", None, QtGui.QApplication.UnicodeUTF8))
        self.uiBackBTN.setToolTip(QtGui.QApplication.translate("Form", "<html><head/><body><p>Go Back</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.uiBackBTN.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xlineedit import XLineEdit

