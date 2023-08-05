# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xquerybuilderwidget\ui\xquerybuilderwidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 283)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.uiQueryAREA = QtGui.QScrollArea(Form)
        self.uiQueryAREA.setFrameShape(QtGui.QFrame.NoFrame)
        self.uiQueryAREA.setWidgetResizable(True)
        self.uiQueryAREA.setObjectName("uiQueryAREA")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 382, 228))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.uiQueryAREA.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.uiQueryAREA, 0, 0, 1, 3)
        self.uiResetBTN = QtGui.QPushButton(Form)
        self.uiResetBTN.setAutoDefault(False)
        self.uiResetBTN.setObjectName("uiResetBTN")
        self.gridLayout.addWidget(self.uiResetBTN, 1, 0, 1, 1)
        self.uiSaveBTN = QtGui.QPushButton(Form)
        self.uiSaveBTN.setAutoDefault(True)
        self.uiSaveBTN.setDefault(True)
        self.uiSaveBTN.setObjectName("uiSaveBTN")
        self.gridLayout.addWidget(self.uiSaveBTN, 1, 1, 1, 1)
        self.uiCancelBTN = QtGui.QPushButton(Form)
        self.uiCancelBTN.setAutoDefault(False)
        self.uiCancelBTN.setObjectName("uiCancelBTN")
        self.gridLayout.addWidget(self.uiCancelBTN, 1, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.uiResetBTN.setText(QtGui.QApplication.translate("Form", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.uiSaveBTN.setText(QtGui.QApplication.translate("Form", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.uiCancelBTN.setText(QtGui.QApplication.translate("Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

