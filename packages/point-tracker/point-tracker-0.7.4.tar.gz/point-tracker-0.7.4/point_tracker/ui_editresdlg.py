# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editresdlg.ui'
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

class Ui_EditResDlg(object):
    def setupUi(self, EditResDlg):
        EditResDlg.setObjectName(_fromUtf8("EditResDlg"))
        EditResDlg.resize(623, 621)
        self.verticalLayout = QtGui.QVBoxLayout(EditResDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pixelSizes = QtGui.QTreeView(EditResDlg)
        self.pixelSizes.setAlternatingRowColors(True)
        self.pixelSizes.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.pixelSizes.setIconSize(QtCore.QSize(64, 64))
        self.pixelSizes.setRootIsDecorated(False)
        self.pixelSizes.setObjectName(_fromUtf8("pixelSizes"))
        self.verticalLayout.addWidget(self.pixelSizes)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.setAll = QtGui.QPushButton(EditResDlg)
        self.setAll.setObjectName(_fromUtf8("setAll"))
        self.horizontalLayout.addWidget(self.setAll)
        self.width = QtGui.QLineEdit(EditResDlg)
        self.width.setMaxLength(20)
        self.width.setObjectName(_fromUtf8("width"))
        self.horizontalLayout.addWidget(self.width)
        self.label_2 = QtGui.QLabel(EditResDlg)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.height = QtGui.QLineEdit(EditResDlg)
        self.height.setMaxLength(20)
        self.height.setObjectName(_fromUtf8("height"))
        self.horizontalLayout.addWidget(self.height)
        spacerItem = QtGui.QSpacerItem(218, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(EditResDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.unit = QtGui.QComboBox(EditResDlg)
        self.unit.setObjectName(_fromUtf8("unit"))
        self.unit.addItem(_fromUtf8(""))
        self.unit.addItem(_fromUtf8(""))
        self.unit.addItem(_fromUtf8(""))
        self.unit.addItem(_fromUtf8(""))
        self.unit.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.unit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(EditResDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(EditResDlg)
        self.unit.setCurrentIndex(3)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EditResDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EditResDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(EditResDlg)

    def retranslateUi(self, EditResDlg):
        EditResDlg.setWindowTitle(_translate("EditResDlg", "Pixel Resolution in Images", None))
        self.setAll.setText(_translate("EditResDlg", "Set scales", None))
        self.width.setText(_translate("EditResDlg", "1", None))
        self.label_2.setText(_translate("EditResDlg", "x", None))
        self.height.setText(_translate("EditResDlg", "1", None))
        self.label.setText(_translate("EditResDlg", "Unit:", None))
        self.unit.setItemText(0, _translate("EditResDlg", "km", None))
        self.unit.setItemText(1, _translate("EditResDlg", "m", None))
        self.unit.setItemText(2, _translate("EditResDlg", "mm", None))
        self.unit.setItemText(3, _translate("EditResDlg", "µm", None))
        self.unit.setItemText(4, _translate("EditResDlg", "nm", None))

