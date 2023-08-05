# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xrichtextedit\ui\xfontpickerwidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(358, 196)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.uiSearchTXT = XLineEdit(Form)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/default/img/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiSearchTXT.setProperty("x_icon", icon)
        self.uiSearchTXT.setProperty("x_cornerRadius", 8)
        self.uiSearchTXT.setObjectName("uiSearchTXT")
        self.gridLayout.addWidget(self.uiSearchTXT, 0, 0, 1, 1)
        self.uiSizeSPN = QtGui.QSpinBox(Form)
        self.uiSizeSPN.setObjectName("uiSizeSPN")
        self.gridLayout.addWidget(self.uiSizeSPN, 0, 1, 1, 1)
        self.uiFontTREE = XTreeWidget(Form)
        self.uiFontTREE.setMinimumSize(QtCore.QSize(340, 152))
        self.uiFontTREE.setRootIsDecorated(False)
        self.uiFontTREE.setProperty("x_showGrid", False)
        self.uiFontTREE.setObjectName("uiFontTREE")
        self.uiFontTREE.headerItem().setText(0, "1")
        self.uiFontTREE.header().setVisible(False)
        self.gridLayout.addWidget(self.uiFontTREE, 1, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.uiSearchTXT, QtCore.SIGNAL("textChanged(QString)"), self.uiFontTREE.filterItems)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.uiSearchTXT.setProperty("x_hint", QtGui.QApplication.translate("Form", "search for fonts...", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xtreewidget import XTreeWidget
from projexui.widgets.xlineedit import XLineEdit

