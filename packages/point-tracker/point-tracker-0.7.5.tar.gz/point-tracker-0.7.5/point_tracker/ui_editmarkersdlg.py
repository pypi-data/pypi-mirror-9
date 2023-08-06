# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editmarkersdlg.ui'
#
# Created: Wed May 14 15:26:22 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_EditMarkersDlg(object):
    def setupUi(self, EditMarkersDlg):
        EditMarkersDlg.setObjectName(_fromUtf8("EditMarkersDlg"))
        EditMarkersDlg.resize(459, 692)
        self.verticalLayout_3 = QtGui.QVBoxLayout(EditMarkersDlg)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.groupBox = QtGui.QGroupBox(EditMarkersDlg)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.markersView = QtGui.QTableView(self.groupBox)
        self.markersView.setAlternatingRowColors(True)
        self.markersView.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        self.markersView.setObjectName(_fromUtf8("markersView"))
        self.horizontalLayout.addWidget(self.markersView)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 138, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.addMarker = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addMarker.sizePolicy().hasHeightForWidth())
        self.addMarker.setSizePolicy(sizePolicy)
        self.addMarker.setMinimumSize(QtCore.QSize(20, 0))
        self.addMarker.setMaximumSize(QtCore.QSize(32, 16777215))
        self.addMarker.setObjectName(_fromUtf8("addMarker"))
        self.verticalLayout.addWidget(self.addMarker)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem1)
        self.removeMarker = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.removeMarker.sizePolicy().hasHeightForWidth())
        self.removeMarker.setSizePolicy(sizePolicy)
        self.removeMarker.setMaximumSize(QtCore.QSize(32, 16777215))
        self.removeMarker.setObjectName(_fromUtf8("removeMarker"))
        self.verticalLayout.addWidget(self.removeMarker)
        spacerItem2 = QtGui.QSpacerItem(20, 138, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.rgbaMode = QtGui.QRadioButton(self.groupBox)
        self.rgbaMode.setChecked(True)
        self.rgbaMode.setObjectName(_fromUtf8("rgbaMode"))
        self.horizontalLayout_2.addWidget(self.rgbaMode)
        self.hsvaMode = QtGui.QRadioButton(self.groupBox)
        self.hsvaMode.setObjectName(_fromUtf8("hsvaMode"))
        self.horizontalLayout_2.addWidget(self.hsvaMode)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(EditMarkersDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(EditMarkersDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EditMarkersDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EditMarkersDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(EditMarkersDlg)

    def retranslateUi(self, EditMarkersDlg):
        EditMarkersDlg.setWindowTitle(_translate("EditMarkersDlg", "Edition of tranfer function markers", None))
        self.groupBox.setTitle(_translate("EditMarkersDlg", "Markers", None))
        self.addMarker.setText(_translate("EditMarkersDlg", "+", None))
        self.removeMarker.setText(_translate("EditMarkersDlg", "-", None))
        self.label.setText(_translate("EditMarkersDlg", "Color mode: ", None))
        self.rgbaMode.setText(_translate("EditMarkersDlg", "RGBA", None))
        self.hsvaMode.setText(_translate("EditMarkersDlg", "HSVA", None))

