# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\dialogs\xaboutdialog\ui\xaboutdialog.ui'
#
# Created: Wed Dec 31 14:09:28 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_XAboutDialog(object):
    def setupUi(self, XAboutDialog):
        XAboutDialog.setObjectName("XAboutDialog")
        XAboutDialog.resize(647, 423)
        self.verticalLayout = QtGui.QVBoxLayout(XAboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiLogoLBL = QtGui.QLabel(XAboutDialog)
        self.uiLogoLBL.setMinimumSize(QtCore.QSize(0, 60))
        self.uiLogoLBL.setMaximumSize(QtCore.QSize(16777215, 60))
        self.uiLogoLBL.setText("")
        self.uiLogoLBL.setObjectName("uiLogoLBL")
        self.verticalLayout.addWidget(self.uiLogoLBL)
        self.uiInfoTXT = QtGui.QTextBrowser(XAboutDialog)
        self.uiInfoTXT.setObjectName("uiInfoTXT")
        self.verticalLayout.addWidget(self.uiInfoTXT)
        self.uiDialogBTNS = QtGui.QDialogButtonBox(XAboutDialog)
        self.uiDialogBTNS.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.uiDialogBTNS.setObjectName("uiDialogBTNS")
        self.verticalLayout.addWidget(self.uiDialogBTNS)

        self.retranslateUi(XAboutDialog)
        QtCore.QObject.connect(self.uiDialogBTNS, QtCore.SIGNAL("accepted()"), XAboutDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(XAboutDialog)

    def retranslateUi(self, XAboutDialog):
        XAboutDialog.setWindowTitle(QtGui.QApplication.translate("XAboutDialog", "About", None, QtGui.QApplication.UnicodeUTF8))

