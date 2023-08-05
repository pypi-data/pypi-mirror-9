# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xmenutemplatewidget\ui\xmenutemplatewidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(566, 313)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtGui.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.XLineEdit = XLineEdit(self.layoutWidget)
        self.XLineEdit.setObjectName("XLineEdit")
        self.verticalLayout.addWidget(self.XLineEdit)
        self.uiActionTREE = XTreeWidget(self.layoutWidget)
        self.uiActionTREE.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.uiActionTREE.setRootIsDecorated(False)
        self.uiActionTREE.setProperty("x_arrowStyle", True)
        self.uiActionTREE.setProperty("x_showGrid", False)
        self.uiActionTREE.setObjectName("uiActionTREE")
        self.uiActionTREE.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiActionTREE)
        self.uiMenuTREE = XTreeWidget(self.splitter)
        self.uiMenuTREE.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiMenuTREE.setAcceptDrops(True)
        self.uiMenuTREE.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.uiMenuTREE.setProperty("x_arrowStyle", True)
        self.uiMenuTREE.setProperty("x_showGrid", False)
        self.uiMenuTREE.setObjectName("uiMenuTREE")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.XLineEdit, QtCore.SIGNAL("textChanged(QString)"), self.uiActionTREE.filterItems)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Edit Menu", None, QtGui.QApplication.UnicodeUTF8))
        self.XLineEdit.setProperty("x_hint", QtGui.QApplication.translate("Form", "filter actions...", None, QtGui.QApplication.UnicodeUTF8))
        self.uiActionTREE.headerItem().setText(0, QtGui.QApplication.translate("Form", "Actions", None, QtGui.QApplication.UnicodeUTF8))
        self.uiMenuTREE.headerItem().setText(0, QtGui.QApplication.translate("Form", "Menu", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xtreewidget import XTreeWidget
from projexui.widgets.xlineedit import XLineEdit
