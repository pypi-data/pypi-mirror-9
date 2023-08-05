# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\workspace\dev\projex\projexui\src\projexui\widgets\xcollapsibleloggerwidget\ui\xcollapsibleloggerwidget.ui'
#
# Created: Wed Dec 31 14:09:29 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_XCollapsibleLoggerWidget(object):
    def setupUi(self, XCollapsibleLoggerWidget):
        XCollapsibleLoggerWidget.setObjectName("XCollapsibleLoggerWidget")
        XCollapsibleLoggerWidget.resize(700, 265)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(XCollapsibleLoggerWidget.sizePolicy().hasHeightForWidth())
        XCollapsibleLoggerWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(XCollapsibleLoggerWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.uiLoggerWGT = XLoggerWidget(XCollapsibleLoggerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.uiLoggerWGT.sizePolicy().hasHeightForWidth())
        self.uiLoggerWGT.setSizePolicy(sizePolicy)
        self.uiLoggerWGT.setProperty("showCollapsed", False)
        self.uiLoggerWGT.setObjectName("uiLoggerWGT")
        self.gridLayout.addWidget(self.uiLoggerWGT, 0, 1, 1, 2)
        self.uiHideBTN = QtGui.QToolButton(XCollapsibleLoggerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiHideBTN.sizePolicy().hasHeightForWidth())
        self.uiHideBTN.setSizePolicy(sizePolicy)
        self.uiHideBTN.setMinimumSize(QtCore.QSize(15, 0))
        self.uiHideBTN.setMaximumSize(QtCore.QSize(15, 16777215))
        self.uiHideBTN.setAutoRaise(True)
        self.uiHideBTN.setArrowType(QtCore.Qt.DownArrow)
        self.uiHideBTN.setProperty("showCollapsed", False)
        self.uiHideBTN.setObjectName("uiHideBTN")
        self.gridLayout.addWidget(self.uiHideBTN, 0, 0, 2, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiShowBTN = QtGui.QToolButton(XCollapsibleLoggerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiShowBTN.sizePolicy().hasHeightForWidth())
        self.uiShowBTN.setSizePolicy(sizePolicy)
        self.uiShowBTN.setMinimumSize(QtCore.QSize(15, 24))
        self.uiShowBTN.setMaximumSize(QtCore.QSize(15, 24))
        self.uiShowBTN.setAutoRaise(True)
        self.uiShowBTN.setArrowType(QtCore.Qt.UpArrow)
        self.uiShowBTN.setProperty("showCollapsed", True)
        self.uiShowBTN.setObjectName("uiShowBTN")
        self.horizontalLayout.addWidget(self.uiShowBTN)
        spacerItem = QtGui.QSpacerItem(6, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiFeedbackLBL = QtGui.QLabel(XCollapsibleLoggerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiFeedbackLBL.sizePolicy().hasHeightForWidth())
        self.uiFeedbackLBL.setSizePolicy(sizePolicy)
        self.uiFeedbackLBL.setMinimumSize(QtCore.QSize(0, 24))
        self.uiFeedbackLBL.setMaximumSize(QtCore.QSize(16777215, 24))
        self.uiFeedbackLBL.setText("")
        self.uiFeedbackLBL.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.uiFeedbackLBL.setProperty("showCollapsed", True)
        self.uiFeedbackLBL.setObjectName("uiFeedbackLBL")
        self.horizontalLayout.addWidget(self.uiFeedbackLBL)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(XCollapsibleLoggerWidget)
        QtCore.QMetaObject.connectSlotsByName(XCollapsibleLoggerWidget)

    def retranslateUi(self, XCollapsibleLoggerWidget):
        XCollapsibleLoggerWidget.setWindowTitle(QtGui.QApplication.translate("XCollapsibleLoggerWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.uiHideBTN.setToolTip(QtGui.QApplication.translate("XCollapsibleLoggerWidget", "<html><head/><body><p><span style=\" font-weight:600;\">Collpase Logger</span></p><p>Hide the logger widget and only show the status label.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.uiHideBTN.setText(QtGui.QApplication.translate("XCollapsibleLoggerWidget", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.uiShowBTN.setToolTip(QtGui.QApplication.translate("XCollapsibleLoggerWidget", "<html><head/><body><p><span style=\" font-weight:600;\">Expand Logger</span></p><p>Click here to view more details and options for the logger.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.uiShowBTN.setText(QtGui.QApplication.translate("XCollapsibleLoggerWidget", "...", None, QtGui.QApplication.UnicodeUTF8))

from projexui.widgets.xloggerwidget import XLoggerWidget

