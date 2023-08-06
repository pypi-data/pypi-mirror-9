# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'alignmentdlg.ui'
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

class Ui_AlignmentDlg(object):
    def setupUi(self, AlignmentDlg):
        AlignmentDlg.setObjectName(_fromUtf8("AlignmentDlg"))
        AlignmentDlg.resize(530, 245)
        self.vboxlayout = QtGui.QVBoxLayout(AlignmentDlg)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.groupBox = QtGui.QGroupBox(AlignmentDlg)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.hboxlayout = QtGui.QHBoxLayout(self.groupBox)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.referencePoint = QtGui.QComboBox(self.groupBox)
        self.referencePoint.setObjectName(_fromUtf8("referencePoint"))
        self.referencePoint.addItem(_fromUtf8(""))
        self.referencePoint.addItem(_fromUtf8(""))
        self.hboxlayout.addWidget(self.referencePoint)
        self.vboxlayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(AlignmentDlg)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox_2)
        self.vboxlayout1.setObjectName(_fromUtf8("vboxlayout1"))
        self.noRotation = QtGui.QRadioButton(self.groupBox_2)
        self.noRotation.setChecked(True)
        self.noRotation.setObjectName(_fromUtf8("noRotation"))
        self.vboxlayout1.addWidget(self.noRotation)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.twoPointsRotation = QtGui.QRadioButton(self.groupBox_2)
        self.twoPointsRotation.setObjectName(_fromUtf8("twoPointsRotation"))
        self.hboxlayout1.addWidget(self.twoPointsRotation)
        self.rotationPt1 = QtGui.QComboBox(self.groupBox_2)
        self.rotationPt1.setEnabled(False)
        self.rotationPt1.setObjectName(_fromUtf8("rotationPt1"))
        self.hboxlayout1.addWidget(self.rotationPt1)
        self.rotationPt2 = QtGui.QComboBox(self.groupBox_2)
        self.rotationPt2.setEnabled(False)
        self.rotationPt2.setObjectName(_fromUtf8("rotationPt2"))
        self.hboxlayout1.addWidget(self.rotationPt2)
        self.vboxlayout1.addLayout(self.hboxlayout1)
        self.vboxlayout.addWidget(self.groupBox_2)
        self.buttonBox = QtGui.QDialogButtonBox(AlignmentDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(AlignmentDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AlignmentDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AlignmentDlg.reject)
        QtCore.QObject.connect(self.twoPointsRotation, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.rotationPt1.setEnabled)
        QtCore.QObject.connect(self.twoPointsRotation, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.rotationPt2.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(AlignmentDlg)

    def retranslateUi(self, AlignmentDlg):
        AlignmentDlg.setWindowTitle(_translate("AlignmentDlg", "Alignment parameters", None))
        self.groupBox.setTitle(_translate("AlignmentDlg", "Translation", None))
        self.label.setText(_translate("AlignmentDlg", "Reference point", None))
        self.referencePoint.setItemText(0, _translate("AlignmentDlg", "Barycentre", None))
        self.referencePoint.setItemText(1, _translate("AlignmentDlg", "Bounding-box centre", None))
        self.groupBox_2.setTitle(_translate("AlignmentDlg", "Rotation", None))
        self.noRotation.setText(_translate("AlignmentDlg", "None", None))
        self.twoPointsRotation.setText(_translate("AlignmentDlg", "Two points", None))

