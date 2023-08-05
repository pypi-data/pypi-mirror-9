# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xprogressfeedbackwidget\ui\xprogressfeedbackwidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_XProgressFeedbackWidget(object):
    def setupUi(self, XProgressFeedbackWidget):
        XProgressFeedbackWidget.setObjectName("XProgressFeedbackWidget")
        XProgressFeedbackWidget.resize(455, 265)
        self.gridLayout = QtGui.QGridLayout(XProgressFeedbackWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.uiFeedbackLBL = QtGui.QLabel(XProgressFeedbackWidget)
        self.uiFeedbackLBL.setObjectName("uiFeedbackLBL")
        self.gridLayout.addWidget(self.uiFeedbackLBL, 0, 0, 1, 1)
        self.uiProgressBAR = QtGui.QProgressBar(XProgressFeedbackWidget)
        self.uiProgressBAR.setMinimumSize(QtCore.QSize(0, 40))
        self.uiProgressBAR.setProperty("value", 24)
        self.uiProgressBAR.setObjectName("uiProgressBAR")
        self.gridLayout.addWidget(self.uiProgressBAR, 1, 0, 1, 1)
        self.uiShowDetailsCHK = QtGui.QCheckBox(XProgressFeedbackWidget)
        self.uiShowDetailsCHK.setObjectName("uiShowDetailsCHK")
        self.gridLayout.addWidget(self.uiShowDetailsCHK, 3, 0, 1, 1)
        self.uiLoggerEDIT = XLoggerWidget(XProgressFeedbackWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.uiLoggerEDIT.sizePolicy().hasHeightForWidth())
        self.uiLoggerEDIT.setSizePolicy(sizePolicy)
        self.uiLoggerEDIT.setProperty("x_configurable", False)
        self.uiLoggerEDIT.setObjectName("uiLoggerEDIT")
        self.gridLayout.addWidget(self.uiLoggerEDIT, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.uiSecondaryProgressBAR = QtGui.QProgressBar(XProgressFeedbackWidget)
        self.uiSecondaryProgressBAR.setMinimumSize(QtCore.QSize(0, 12))
        self.uiSecondaryProgressBAR.setMaximumSize(QtCore.QSize(16777215, 12))
        font = QtGui.QFont()
        font.setPointSize(6)
        self.uiSecondaryProgressBAR.setFont(font)
        self.uiSecondaryProgressBAR.setProperty("value", 24)
        self.uiSecondaryProgressBAR.setObjectName("uiSecondaryProgressBAR")
        self.gridLayout.addWidget(self.uiSecondaryProgressBAR, 2, 0, 1, 1)

        self.retranslateUi(XProgressFeedbackWidget)
        QtCore.QObject.connect(self.uiShowDetailsCHK, QtCore.SIGNAL("toggled(bool)"), self.uiLoggerEDIT.setVisible)
        QtCore.QMetaObject.connectSlotsByName(XProgressFeedbackWidget)

    def retranslateUi(self, XProgressFeedbackWidget):
        XProgressFeedbackWidget.setWindowTitle(QtGui.QApplication.translate("XProgressFeedbackWidget", "Progress", None, QtGui.QApplication.UnicodeUTF8))
        self.uiFeedbackLBL.setText(QtGui.QApplication.translate("XProgressFeedbackWidget", "Installing plugins...", None, QtGui.QApplication.UnicodeUTF8))
        self.uiShowDetailsCHK.setText(QtGui.QApplication.translate("XProgressFeedbackWidget", "Show details", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xloggerwidget import XLoggerWidget
