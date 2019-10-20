# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mosaicpy/gui/frame.ui',
# licensing of 'mosaicpy/gui/frame.ui' applies.
#
# Created: Sat Oct 19 07:57:32 2019
#      by: pyside2-uic  running on PySide2 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_impFrame(object):
    def setupUi(self, impFrame):
        impFrame.setObjectName("impFrame")
        impFrame.resize(288, 38)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(impFrame.sizePolicy().hasHeightForWidth())
        impFrame.setSizePolicy(sizePolicy)
        impFrame.setStyleSheet("* {font-family: avenir, \"century gothic\"; color: #222;}\n"
"#title {font-size: 13px; font-weight: bold;}\n"
":disabled {color:rgba(0,0,0,80);}\n"
"#impFrame { background: qlineargradient(spread:pad, x1:0 y1:1, x2:0 y2:0, stop:0 rgba(190, 190, 190), stop:1 rgba(220,220,220)) }\n"
"QLabel { qproperty-alignment: AlignRight; }\n"
"#closeButton{ font-size: 20pt; padding-left: 6;  padding-right: 6; padding-bottom: 2px; }\n"
"#helpButton{ color: #555; font-size: 14pt; padding-left: 6; padding-right: 8;}\n"
"#closeButton:hover:!pressed {color: red;}\n"
"#helpButton:hover:!pressed {color: red;}\n"
"")
        impFrame.setFrameShape(QtWidgets.QFrame.Panel)
        impFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(impFrame)
        self.verticalLayout_2.setSpacing(1)
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLayout.setContentsMargins(-1, 0, 0, 0)
        self.titleLayout.setObjectName("titleLayout")
        self.arrowFrame = QtWidgets.QFrame(impFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.arrowFrame.sizePolicy().hasHeightForWidth())
        self.arrowFrame.setSizePolicy(sizePolicy)
        self.arrowFrame.setMinimumSize(QtCore.QSize(24, 16))
        self.arrowFrame.setMaximumSize(QtCore.QSize(24, 24))
        self.arrowFrame.setStyleSheet("border: 0px;")
        self.arrowFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.arrowFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.arrowFrame.setObjectName("arrowFrame")
        self.titleLayout.addWidget(self.arrowFrame)
        self.activeBox = QtWidgets.QCheckBox(impFrame)
        self.activeBox.setMinimumSize(QtCore.QSize(34, 16))
        self.activeBox.setMaximumSize(QtCore.QSize(34, 16777215))
        self.activeBox.setText("")
        self.activeBox.setChecked(True)
        self.activeBox.setObjectName("activeBox")
        self.titleLayout.addWidget(self.activeBox)
        self.title = QtWidgets.QLabel(impFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.title.sizePolicy().hasHeightForWidth())
        self.title.setSizePolicy(sizePolicy)
        self.title.setBaseSize(QtCore.QSize(0, 0))
        self.title.setObjectName("title")
        self.titleLayout.addWidget(self.title)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.titleLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.titleLayout)
        self.content = QtWidgets.QWidget(impFrame)
        self.content.setObjectName("content")
        self.contentLayout = QtWidgets.QGridLayout(self.content)
        self.contentLayout.setContentsMargins(-1, 0, -1, 10)
        self.contentLayout.setVerticalSpacing(4)
        self.contentLayout.setObjectName("contentLayout")
        self.verticalLayout_2.addWidget(self.content)

        self.retranslateUi(impFrame)
        QtCore.QObject.connect(self.activeBox, QtCore.SIGNAL("toggled(bool)"), self.content.setEnabled)
        QtCore.QObject.connect(self.activeBox, QtCore.SIGNAL("toggled(bool)"), self.title.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(impFrame)

    def retranslateUi(self, impFrame):
        impFrame.setWindowTitle(QtWidgets.QApplication.translate("impFrame", "Frame", None, -1))
        self.title.setText(QtWidgets.QApplication.translate("impFrame", "TextLabel", None, -1))

