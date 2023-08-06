# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timeeditdlg.ui'
#
# Created: Wed May 14 15:26:23 2014
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

class Ui_TimeEditDlg(object):
    def setupUi(self, TimeEditDlg):
        TimeEditDlg.setObjectName(_fromUtf8("TimeEditDlg"))
        TimeEditDlg.resize(581, 463)
        self.verticalLayout = QtGui.QVBoxLayout(TimeEditDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.imagesTiming = QtGui.QTreeView(TimeEditDlg)
        self.imagesTiming.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        self.imagesTiming.setIconSize(QtCore.QSize(64, 64))
        self.imagesTiming.setRootIsDecorated(False)
        self.imagesTiming.setObjectName(_fromUtf8("imagesTiming"))
        self.verticalLayout.addWidget(self.imagesTiming)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(TimeEditDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.deltaTime = QtGui.QLineEdit(TimeEditDlg)
        self.deltaTime.setObjectName(_fromUtf8("deltaTime"))
        self.horizontalLayout.addWidget(self.deltaTime)
        self.resetTiming = QtGui.QPushButton(TimeEditDlg)
        self.resetTiming.setObjectName(_fromUtf8("resetTiming"))
        self.horizontalLayout.addWidget(self.resetTiming)
        spacerItem = QtGui.QSpacerItem(102, 28, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(TimeEditDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(TimeEditDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TimeEditDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TimeEditDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(TimeEditDlg)

    def retranslateUi(self, TimeEditDlg):
        TimeEditDlg.setWindowTitle(_translate("TimeEditDlg", "Dialog", None))
        self.label.setText(_translate("TimeEditDlg", "Regular timing", None))
        self.deltaTime.setInputMask(_translate("TimeEditDlg", "ddddd9\\h09mi\\n; ", None))
        self.deltaTime.setText(_translate("TimeEditDlg", "0h30min", None))
        self.resetTiming.setText(_translate("TimeEditDlg", "Set", None))

from . import icons_rc
