# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xviewwidget\ui\xviewprofiledialog.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 175)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiIconBTN = XIconButton(Dialog)
        self.uiIconBTN.setIconSize(QtCore.QSize(48, 48))
        self.uiIconBTN.setObjectName("uiIconBTN")
        self.gridLayout.addWidget(self.uiIconBTN, 0, 0, 2, 1)
        self.uiNameLBL = QtGui.QLabel(Dialog)
        self.uiNameLBL.setObjectName("uiNameLBL")
        self.gridLayout.addWidget(self.uiNameLBL, 0, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiNameTXT = QtGui.QLineEdit(Dialog)
        self.uiNameTXT.setObjectName("uiNameTXT")
        self.horizontalLayout.addWidget(self.uiNameTXT)
        self.uiVersionSPN = QtGui.QDoubleSpinBox(Dialog)
        self.uiVersionSPN.setDecimals(1)
        self.uiVersionSPN.setMinimum(1.0)
        self.uiVersionSPN.setObjectName("uiVersionSPN")
        self.horizontalLayout.addWidget(self.uiVersionSPN)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 2, 1, 1)
        self.uiDescriptionLBL = QtGui.QLabel(Dialog)
        self.uiDescriptionLBL.setObjectName("uiDescriptionLBL")
        self.gridLayout.addWidget(self.uiDescriptionLBL, 1, 1, 1, 1)
        self.uiDescriptionTXT = QtGui.QTextEdit(Dialog)
        self.uiDescriptionTXT.setObjectName("uiDescriptionTXT")
        self.gridLayout.addWidget(self.uiDescriptionTXT, 1, 2, 2, 1)
        spacerItem = QtGui.QSpacerItem(20, 24, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.uiDialogBTNS = QtGui.QDialogButtonBox(Dialog)
        self.uiDialogBTNS.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiDialogBTNS.setObjectName("uiDialogBTNS")
        self.gridLayout.addWidget(self.uiDialogBTNS, 3, 0, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.uiDialogBTNS, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.uiDialogBTNS, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Edit Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.uiNameLBL.setText(QtGui.QApplication.translate("Dialog", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.uiVersionSPN.setPrefix(QtGui.QApplication.translate("Dialog", "v", None, QtGui.QApplication.UnicodeUTF8))
        self.uiDescriptionLBL.setText(QtGui.QApplication.translate("Dialog", "Description:", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xiconbutton import XIconButton
