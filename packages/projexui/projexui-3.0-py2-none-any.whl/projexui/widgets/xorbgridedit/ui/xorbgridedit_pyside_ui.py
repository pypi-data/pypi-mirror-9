# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xorbgridedit\ui\xorbgridedit.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(563, 286)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.uiToolbarLAYOUT = QtGui.QHBoxLayout()
        self.uiToolbarLAYOUT.setSpacing(3)
        self.uiToolbarLAYOUT.setObjectName("uiToolbarLAYOUT")
        self.uiSearchTXT = XLineEdit(Form)
        self.uiSearchTXT.setMinimumSize(QtCore.QSize(0, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.uiSearchTXT.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/default/img/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiSearchTXT.setProperty("x_icon", icon)
        self.uiSearchTXT.setProperty("x_cornerRadius", 10)
        self.uiSearchTXT.setObjectName("uiSearchTXT")
        self.uiToolbarLAYOUT.addWidget(self.uiSearchTXT)
        self.uiQueryBTN = XPopupButton(Form)
        self.uiQueryBTN.setMaximumSize(QtCore.QSize(26, 26))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/default/img/query/query.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiQueryBTN.setIcon(icon1)
        self.uiQueryBTN.setIconSize(QtCore.QSize(24, 24))
        self.uiQueryBTN.setAutoRaise(True)
        self.uiQueryBTN.setObjectName("uiQueryBTN")
        self.uiToolbarLAYOUT.addWidget(self.uiQueryBTN)
        self.uiRefreshBTN = QtGui.QToolButton(Form)
        self.uiRefreshBTN.setMinimumSize(QtCore.QSize(26, 26))
        self.uiRefreshBTN.setMaximumSize(QtCore.QSize(26, 26))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/default/img/query/reload.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiRefreshBTN.setIcon(icon2)
        self.uiRefreshBTN.setIconSize(QtCore.QSize(24, 24))
        self.uiRefreshBTN.setAutoRaise(True)
        self.uiRefreshBTN.setObjectName("uiRefreshBTN")
        self.uiToolbarLAYOUT.addWidget(self.uiRefreshBTN)
        self.uiSaveBTN = QtGui.QPushButton(Form)
        self.uiSaveBTN.setMinimumSize(QtCore.QSize(100, 26))
        self.uiSaveBTN.setObjectName("uiSaveBTN")
        self.uiToolbarLAYOUT.addWidget(self.uiSaveBTN)
        self.gridLayout.addLayout(self.uiToolbarLAYOUT, 0, 0, 1, 1)
        self.uiRecordTREE = XOrbTreeWidget(Form)
        self.uiRecordTREE.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.uiRecordTREE.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.uiRecordTREE.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.uiRecordTREE.setProperty("x_paged", True)
        self.uiRecordTREE.setObjectName("uiRecordTREE")
        self.uiRecordTREE.headerItem().setText(0, "1")
        self.gridLayout.addWidget(self.uiRecordTREE, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.uiSearchTXT, QtCore.SIGNAL("textEntered(QString)"), self.uiRecordTREE.searchRecords)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Edit Records", None, QtGui.QApplication.UnicodeUTF8))
        self.uiSearchTXT.setProperty("x_hint", QtGui.QApplication.translate("Form", "search records", None, QtGui.QApplication.UnicodeUTF8))
        self.uiQueryBTN.setToolTip(QtGui.QApplication.translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">Configure Query</span></p><p>Configure the query options for this editor</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRefreshBTN.setToolTip(QtGui.QApplication.translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">Refresh Results</span></p><p>Reloads/Refreshes the results from the database</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRefreshBTN.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.uiSaveBTN.setToolTip(QtGui.QApplication.translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">Save Changes</span></p><p>Commits your changes to the database</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.uiSaveBTN.setText(QtGui.QApplication.translate("Form", "Save Changes", None, QtGui.QApplication.UnicodeUTF8))
        self.uiRecordTREE.setProperty("x_hint", QtGui.QApplication.translate("Form", "No records were found.  You can define your search query through the query popup button in the top right corner.", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xpopupbutton import XPopupButton
from projexui.widgets.xorbtreewidget import XOrbTreeWidget
from projexui.widgets.xlineedit import XLineEdit

