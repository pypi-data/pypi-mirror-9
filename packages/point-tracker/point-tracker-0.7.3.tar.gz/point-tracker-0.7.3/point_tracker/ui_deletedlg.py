# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deletedlg.ui'
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

class Ui_DeleteDlg(object):
    def setupUi(self, DeleteDlg):
        DeleteDlg.setObjectName(_fromUtf8("DeleteDlg"))
        DeleteDlg.resize(532, 79)
        self.vboxlayout = QtGui.QVBoxLayout(DeleteDlg)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.label = QtGui.QLabel(DeleteDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.vboxlayout.addWidget(self.label)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.inAllImages = QtGui.QPushButton(DeleteDlg)
        self.inAllImages.setCheckable(True)
        self.inAllImages.setObjectName(_fromUtf8("inAllImages"))
        self.hboxlayout.addWidget(self.inAllImages)
        self.toImage = QtGui.QPushButton(DeleteDlg)
        self.toImage.setCheckable(True)
        self.toImage.setObjectName(_fromUtf8("toImage"))
        self.hboxlayout.addWidget(self.toImage)
        self.fromImage = QtGui.QPushButton(DeleteDlg)
        self.fromImage.setCheckable(True)
        self.fromImage.setObjectName(_fromUtf8("fromImage"))
        self.hboxlayout.addWidget(self.fromImage)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.retranslateUi(DeleteDlg)
        QtCore.QObject.connect(self.inAllImages, QtCore.SIGNAL(_fromUtf8("clicked()")), DeleteDlg.accept)
        QtCore.QObject.connect(self.toImage, QtCore.SIGNAL(_fromUtf8("clicked()")), DeleteDlg.accept)
        QtCore.QObject.connect(self.fromImage, QtCore.SIGNAL(_fromUtf8("clicked()")), DeleteDlg.accept)
        QtCore.QMetaObject.connectSlotsByName(DeleteDlg)

    def retranslateUi(self, DeleteDlg):
        DeleteDlg.setWindowTitle(_translate("DeleteDlg", "Delete selecting point", None))
        self.label.setText(_translate("DeleteDlg", "Deleting selected points", None))
        self.inAllImages.setText(_translate("DeleteDlg", "In all images", None))
        self.toImage.setText(_translate("DeleteDlg", "Up to image", None))
        self.fromImage.setText(_translate("DeleteDlg", "Starting from image", None))

