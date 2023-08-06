# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'copy_progress.ui'
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

class Ui_CopyProgress(object):
    def setupUi(self, CopyProgress):
        CopyProgress.setObjectName(_fromUtf8("CopyProgress"))
        CopyProgress.resize(393, 178)
        self.vboxlayout = QtGui.QVBoxLayout(CopyProgress)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.label = QtGui.QLabel(CopyProgress)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.vboxlayout.addWidget(self.label)
        self.imageProgress = QtGui.QProgressBar(CopyProgress)
        self.imageProgress.setProperty("value", 0)
        self.imageProgress.setObjectName(_fromUtf8("imageProgress"))
        self.vboxlayout.addWidget(self.imageProgress)
        self.label_2 = QtGui.QLabel(CopyProgress)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.vboxlayout.addWidget(self.label_2)
        self.pointProgress = QtGui.QProgressBar(CopyProgress)
        self.pointProgress.setProperty("value", 0)
        self.pointProgress.setObjectName(_fromUtf8("pointProgress"))
        self.vboxlayout.addWidget(self.pointProgress)
        self.buttonBox = QtGui.QDialogButtonBox(CopyProgress)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Abort)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(CopyProgress)
        QtCore.QMetaObject.connectSlotsByName(CopyProgress)

    def retranslateUi(self, CopyProgress):
        CopyProgress.setWindowTitle(_translate("CopyProgress", "Copy points progress", None))
        self.label.setText(_translate("CopyProgress", "Images processed", None))
        self.label_2.setText(_translate("CopyProgress", "Points processed", None))

