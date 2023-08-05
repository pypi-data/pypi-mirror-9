# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\wizards\xscaffoldwizard\ui\xscaffoldstructurepage.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_XScaffoldStructurePage(object):
    def setupUi(self, XScaffoldStructurePage):
        XScaffoldStructurePage.setObjectName("XScaffoldStructurePage")
        XScaffoldStructurePage.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(XScaffoldStructurePage)
        self.gridLayout.setObjectName("gridLayout")
        self.uiOutputPATH = XFilepathEdit(XScaffoldStructurePage)
        self.uiOutputPATH.setObjectName("uiOutputPATH")
        self.gridLayout.addWidget(self.uiOutputPATH, 0, 0, 1, 1)
        self.uiStructureTREE = XTreeWidget(XScaffoldStructurePage)
        self.uiStructureTREE.setProperty("x_arrowStyle", True)
        self.uiStructureTREE.setProperty("x_showGrid", False)
        self.uiStructureTREE.setObjectName("uiStructureTREE")
        self.gridLayout.addWidget(self.uiStructureTREE, 1, 0, 1, 1)

        self.retranslateUi(XScaffoldStructurePage)
        QtCore.QMetaObject.connectSlotsByName(XScaffoldStructurePage)

    def retranslateUi(self, XScaffoldStructurePage):
        XScaffoldStructurePage.setWindowTitle(QtGui.QApplication.translate("XScaffoldStructurePage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        XScaffoldStructurePage.setTitle(QtGui.QApplication.translate("XScaffoldStructurePage", "Structure", None, QtGui.QApplication.UnicodeUTF8))
        XScaffoldStructurePage.setSubTitle(QtGui.QApplication.translate("XScaffoldStructurePage", "Setup filesystem structure before creation", None, QtGui.QApplication.UnicodeUTF8))
        self.uiOutputPATH.setProperty("x_filepathModeText", QtGui.QApplication.translate("XScaffoldStructurePage", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.uiStructureTREE.setProperty("x_hint", QtGui.QApplication.translate("XScaffoldStructurePage", "No structure defined.", None, QtGui.QApplication.UnicodeUTF8))
        self.uiStructureTREE.headerItem().setText(0, QtGui.QApplication.translate("XScaffoldStructurePage", "Structure", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xfilepathedit import XFilepathEdit
from projexui.widgets.xtreewidget import XTreeWidget
