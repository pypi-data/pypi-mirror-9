# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xquerybuilderwidget\ui\xquerylinewidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(462, 25)
        Form.setMinimumSize(QtCore.QSize(460, 24))
        Form.setMaximumSize(QtCore.QSize(16777215, 25))
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiTermDDL = QtGui.QComboBox(Form)
        self.uiTermDDL.setMinimumSize(QtCore.QSize(120, 0))
        self.uiTermDDL.setMaximumSize(QtCore.QSize(120, 16777215))
        self.uiTermDDL.setObjectName("uiTermDDL")
        self.horizontalLayout.addWidget(self.uiTermDDL)
        spacerItem = QtGui.QSpacerItem(6, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiOperatorDDL = QtGui.QComboBox(Form)
        self.uiOperatorDDL.setMinimumSize(QtCore.QSize(80, 0))
        self.uiOperatorDDL.setMaximumSize(QtCore.QSize(80, 16777215))
        self.uiOperatorDDL.setObjectName("uiOperatorDDL")
        self.horizontalLayout.addWidget(self.uiOperatorDDL)
        spacerItem1 = QtGui.QSpacerItem(6, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.uiWidgetAREA = QtGui.QScrollArea(Form)
        self.uiWidgetAREA.setMinimumSize(QtCore.QSize(0, 24))
        self.uiWidgetAREA.setMaximumSize(QtCore.QSize(16777215, 24))
        self.uiWidgetAREA.setFrameShape(QtGui.QFrame.NoFrame)
        self.uiWidgetAREA.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.uiWidgetAREA.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.uiWidgetAREA.setWidgetResizable(True)
        self.uiWidgetAREA.setObjectName("uiWidgetAREA")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 204, 24))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.uiWidgetAREA.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.uiWidgetAREA)
        self.uiRemoveBTN = QtGui.QToolButton(Form)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/default/img/remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiRemoveBTN.setIcon(icon)
        self.uiRemoveBTN.setAutoRaise(True)
        self.uiRemoveBTN.setObjectName("uiRemoveBTN")
        self.horizontalLayout.addWidget(self.uiRemoveBTN)
        self.uiAddBTN = QtGui.QToolButton(Form)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/default/img/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiAddBTN.setIcon(icon1)
        self.uiAddBTN.setAutoRaise(True)
        self.uiAddBTN.setObjectName("uiAddBTN")
        self.horizontalLayout.addWidget(self.uiAddBTN)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRemoveBTN.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.uiAddBTN.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))


